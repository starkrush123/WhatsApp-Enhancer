import appModuleHandler
from scriptHandler import script
import ui
import api
import controlTypes
import config
import sys
import re
import logHandler
import speech
import speechViewer
import tones
import globalCommands

sys.path.insert(0, ".")
from .text_window import TextWindow
from .wh_observers import TitleObserver, ChatObserver, ProgressObserver
from .wh_navigation import (
	focus_chats, 
	focus_messages, 
	focus_composer, 
	perform_voice_call, 
	perform_video_call
)
from .wh_utils import find_by_automation_id

class AppModule(appModuleHandler.AppModule):
	disableBrowseModeByDefault = True
	mainWindow = None
	scriptCategory = _("WhatsApp Enhancer")
	
	_message_list_cache = None
	_title_element_cache = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._last_spoken_text = ""
		self._review_cursor = 0
		self._is_reviewing = False
		self._original_speak = None
		self._patch_speech()

		try:
			conf = config.conf["WhatsAppEnhancer"]
			if conf.get("automaticReadingOfNewMessages") and not ChatObserver.active:
				ChatObserver.restore(self)
		except (KeyError, AttributeError):
			# Config not ready yet
			pass

	@script(
		description=_("Toggle phone number filtering in speech"),
		gesture="kb:control+shift+e"
	)
	def script_togglePhoneFilter(self, gesture):
		# Toggle configuration directly
		try:
			current_val = config.conf["WhatsAppEnhancer"]["filter_phone_numbers"]
			new_val = not current_val
			config.conf["WhatsAppEnhancer"]["filter_phone_numbers"] = new_val
			state = _("on") if new_val else _("off")
			ui.message(_("Phone number filtering {state}").format(state=state))
		except KeyError:
			ui.message(_("Error accessing configuration"))

	def event_NVDAObject_init(self, obj):
		if obj.role == controlTypes.Role.SECTION:
			obj.role = controlTypes.Role.PANE

	def event_gainFocus(self, obj, nextHandler):
		if obj.treeInterceptor:
			obj.treeInterceptor.passThrough = True
		
		if not self.mainWindow or not self.mainWindow.windowHandle:
			curr = obj
			while curr and curr.role != controlTypes.Role.WINDOW:
				if not curr.parent: break
				curr = curr.parent
			if curr and curr.role == controlTypes.Role.WINDOW:
				self.mainWindow = curr

		try:
			conf = config.conf["WhatsAppEnhancer"]
			if conf.get("automaticReadingOfNewMessages") and ChatObserver.paused:
				ChatObserver.restore(self)
		except (KeyError, AttributeError):
			pass

		nextHandler()

	def terminate(self):
		self._unpatch_speech()
		super().terminate()

	def _patch_speech(self):
		try:
			self._original_speak = speech.speech.speak
			speech.speech.speak = self._on_speak
		except AttributeError:
			self._original_speak = speech.speak
			speech.speak = self._on_speak

	def _unpatch_speech(self):
		if self._original_speak:
			try:
				speech.speech.speak = self._original_speak
			except AttributeError:
				speech.speak = self._original_speak

	def _on_speak(self, sequence, *args, **kwargs):
		new_sequence = []
		
		# Phone number regex: + followed by digits, spaces, or dashes
		phone_pattern = r'\+\d[\d\s-]{6,}\d'

		def filter_phone(match):
			full_text = match.string
			start_index = match.start()
			end_index = match.end()
			
			prefix = full_text[:start_index].strip()
			
			# Keep if start of string (just a number)
			if not prefix:
				return match.group(0)

			# Keep if comma-separated list (likely multiple contacts/numbers)
			if prefix.endswith(','):
				return match.group(0)

			# Keep if it looks like a label (e.g. "Number: +62...")
			if prefix.endswith(':'):
				return match.group(0)

			# Smart Filter: Always remove if it contains "Mungkin" (Maybe) -> Unsaved contact header
			if "mungkin" in prefix.lower():
				return ""

			suffix = full_text[end_index:].strip()
			if not suffix:
				return "" # Remove trailing numbers in headers

			# Smart Filter: Remove if followed by URL
			if suffix.lower().startswith("http"):
				return ""

			# Existing: Remove if followed by Digit (Time) or Uppercase (Header like "Message")
			if suffix[0].isdigit() or suffix[0].isupper():
				return ""
			
			# Smart Filter: Remove if the prefix looks like a Name (ends with Title Case/Upper word)
			# e.g. "Devi Sri Utami +62..." -> Filter
			# "Call me at +62..." -> Keep ("at" is lower)
			words = prefix.split()
			if words and words[-1][0].isupper():
				return ""
			
			# Keep otherwise (likely notification sentence or meaningful text)
			return match.group(0)

		for item in sequence:
			# Check config directly for instant update
			is_filtering_enabled = config.conf["WhatsAppEnhancer"].get("filter_phone_numbers", True)
			
			if is_filtering_enabled and isinstance(item, str):
				item = re.sub(phone_pattern, filter_phone, item)
			new_sequence.append(item)

		if self._original_speak:
			self._original_speak(new_sequence, *args, **kwargs)
		
		if self._is_reviewing:
			return

		text_list = [item for item in new_sequence if isinstance(item, str)]
		full_text = " ".join(text_list)
		
		if full_text.strip():
			self._last_spoken_text = full_text
			self._review_cursor = 0

		text_list = []
		for item in new_sequence:
			if isinstance(item, str):
				text_list.append(item)
		
		full_text = " ".join(text_list)
		if full_text.strip():
			self._last_spoken_text = full_text
			self._review_cursor = 0

	@script(
		description=_("Review previous character of last spoken text"),
		gesture="kb:NVDA+leftArrow"
	)
	def script_review_previous_character(self, gesture):
		if not self._last_spoken_text:
			return
		
		self._is_reviewing = True
		try:
			if self._review_cursor > 0:
				self._review_cursor -= 1
				char = self._last_spoken_text[self._review_cursor]
				speech.speak([char])
			else:
				tones.beep(100, 50)
				char = self._last_spoken_text[0]
				speech.speak([char])
		finally:
			self._is_reviewing = False

	@script(
		description=_("Review next character of last spoken text"),
		gesture="kb:NVDA+rightArrow"
	)
	def script_review_next_character(self, gesture):
		if not self._last_spoken_text:
			return

		self._is_reviewing = True
		try:
			if self._review_cursor < len(self._last_spoken_text) - 1:
				self._review_cursor += 1
				char = self._last_spoken_text[self._review_cursor]
				speech.speak([char])
			else:
				tones.beep(400, 50)
				char = self._last_spoken_text[-1]
				speech.speak([char])
		finally:
			self._is_reviewing = False

	@script(
		description=_("Review previous word of last spoken text"),
		gesture="kb:NVDA+control+leftArrow"
	)
	def script_review_previous_word(self, gesture):
		if not self._last_spoken_text:
			return

		self._is_reviewing = True
		try:
			if self._review_cursor <= 0:
				tones.beep(100, 50)
				first_word_end = 0
				while first_word_end < len(self._last_spoken_text) and not self._last_spoken_text[first_word_end].isspace():
					first_word_end += 1
				word = self._last_spoken_text[0:first_word_end]
				if word:
					speech.speak([word])
				return

			cur = self._review_cursor - 1
			
			while cur >= 0 and self._last_spoken_text[cur].isspace():
				cur -= 1
			
			word_end = cur + 1
			while cur >= 0 and not self._last_spoken_text[cur].isspace():
				cur -= 1
			word_start = cur + 1

			word = self._last_spoken_text[word_start:word_end]
			if word:
				self._review_cursor = word_start
				speech.speak([word])
			else:
				tones.beep(100, 50)
		finally:
			self._is_reviewing = False

	@script(
		description=_("Review next word of last spoken text"),
		gesture="kb:NVDA+control+rightArrow"
	)
	def script_review_next_word(self, gesture):
		if not self._last_spoken_text:
			return

		self._is_reviewing = True
		try:
			cur = self._review_cursor
			length = len(self._last_spoken_text)

			while cur < length and not self._last_spoken_text[cur].isspace():
				cur += 1
			
			while cur < length and self._last_spoken_text[cur].isspace():
				cur += 1
			
			if cur >= length:
				tones.beep(400, 50)
				last_word_start = length - 1
				while last_word_start >= 0 and self._last_spoken_text[last_word_start].isspace():
					last_word_start -= 1
				word_start = last_word_start
				while word_start >= 0 and not self._last_spoken_text[word_start].isspace():
					word_start -= 1
				last_word = self._last_spoken_text[word_start+1:last_word_start+1]
				if last_word:
					speech.speak([last_word])
				return

			word_start = cur
			word_end = cur
			while word_end < length and not self._last_spoken_text[word_end].isspace():
				word_end += 1
			
			word = self._last_spoken_text[word_start:word_end]
			if word:
				self._review_cursor = word_start
				speech.speak([word])
			else:
				tones.beep(400, 50)
		finally:
			self._is_reviewing = False

	def get_messages_element(self):
		if self._message_list_cache and self._message_list_cache.location:
			return self._message_list_cache
		
		found = find_by_automation_id(self.mainWindow, "MessagesList")
		if found:
			self._message_list_cache = found[0]
			return found[0]
		return None

	def get_title_element(self):
		if self._title_element_cache and self._title_element_cache.location:
			return self._title_element_cache
		
		found = find_by_automation_id(self.mainWindow, "TitleButton")
		if found:
			self._title_element_cache = found[0]
			return found[0]
		return None

	def is_own_message(self, message_obj):
		return False

	def focus_and_read_message(self, message_obj):
		message_obj.setFocus()
		ui.message(message_obj.name)

	@script(
		description=_("Focus the chat list"),
		gesture="kb:alt+1"
	)
	def script_focusChats(self, gesture):
		focus_chats(self)

	@script(
		description=_("Focus the message composer"),
		gesture="kb:alt+d"
	)
	def script_focusComposer(self, gesture):
		focus_composer(self)

	@script(
		description=_("Focus the message list"),
		gesture="kb:alt+2"
	)
	def script_focusMessages(self, gesture):
		focus_messages(self)

	@script(
		description=_("Report accessibility properties of focused object"),
		gesture="kb:NVDA+shift+i"
	)
	def script_inspector(self, gesture):
		obj = api.getFocusObject()
		role_str = str(obj.role)
		loc = obj.location
		loc_str = f"L:{loc.left}, T:{loc.top}, W:{loc.width}, H:{loc.height}" if loc else "No Loc"
		msg = f"Role: {obj.role} ({obj.role.value}), {loc_str}, Name: '{obj.name}', ID: {obj.UIAAutomationId}"
		ui.message(msg)
		logHandler.log.info(f"WH_INSPECTOR: {msg}")

	@script(
		description=_("Read current chat title. Double press to toggle activity tracking."),
		gesture="kb:alt+t"
	)
	def script_read_profile_name(self, gesture):
		if not self.get_title_element():
			ui.message("Chat title not found")
			return
		
		from scriptHandler import getLastScriptRepeatCount
		if getLastScriptRepeatCount() == 1:
			if TitleObserver.toggle(self):
				ui.message("Chat activity tracking enabled")
			else:
				ui.message("Chat activity tracking disabled")
			return

		title_el = self.get_title_element()
		parts = [child.name for child in title_el.children if child.name]
		ui.message(", ".join(parts))

	@script(
		description=_("Toggle automatic reading of new messages"),
		gesture="kb:alt+l"
	)
	def script_toggle_live_chat(self, gesture):
		if ChatObserver.toggle(self):
			ui.message("Automatic new message reading enabled")
		else:
			ui.message("Automatic new message reading disabled")

	@script(
		description=_("Open current message in a dedicated text window"),
		gesture="kb:alt+c"
	)
	def script_show_text_message(self, gesture):
		obj = api.getFocusObject()
		text = obj.name
		if not text:
			gesture.send()
			return
		TextWindow(text.strip(), "Message Text", readOnly=False)

	@script(
		description=_("Copy current message to clipboard"),
		gesture="kb:control+c"
	)
	def script_copyMessage(self, gesture):
		obj = api.getFocusObject()
		if obj.role == controlTypes.Role.LISTITEM and obj.name:
			api.copyToClip(obj.name.strip())
			ui.message("Copied")
		else:
			gesture.send()

	@script(
		description=_("Initiate voice call"),
		gesture="kb:shift+alt+c"
	)
	def script_call(self, gesture):
		perform_voice_call(self)

	@script(
		description=_("Initiate video call"),
		gesture="kb:shift+alt+v"
	)
	def script_videoCall(self, gesture):
		perform_video_call(self)

	@script(
		description=_("Moves to the next object in a flattened view of the object navigation hierarchy"),
		gesture="kb:control+]"
	)
	def script_nextObject(self, gesture):
		# Mencoba memanggil script flattened view, kalau nggak ada fallback ke navigasi objek biasa
		script = getattr(globalCommands.commands, "script_nextObject", None)
		if not script:
			script = getattr(globalCommands.commands, "script_next", None)
		
		if script:
			script(gesture)
		else:
			gesture.send()

	@script(
		description=_("Moves to the previous object in a flattened view of the object navigation hierarchy"),
		gesture="kb:control+["
	)
	def script_previousObject(self, gesture):
		script = getattr(globalCommands.commands, "script_previousObject", None)
		if not script:
			script = getattr(globalCommands.commands, "script_previous", None)
		
		if script:
			script(gesture)
		else:
			gesture.send()

	@script(
		description=_("Prevents accidental toggling of Browse Mode in WhatsApp"),
		gesture="kb:NVDA+space"
	)
	def script_disableBrowseModeToggle(self, gesture):
		# WhatsApp Desktop (WebView2) works best in Focus Mode.
		# Accidental enabling of Browse Mode breaks navigation.
		# We intercept NVDA+Space and force Focus Mode if not already active.
		if not self.treeInterceptor or not self.treeInterceptor.passThrough:
			if self.treeInterceptor:
				self.treeInterceptor.passThrough = True
			ui.message(_("Browse Mode is disabled for WhatsApp to ensure best experience."))
		else:
			# If already in correct mode, just report it to reassure user
			ui.message(_("Browse Mode disabled"))