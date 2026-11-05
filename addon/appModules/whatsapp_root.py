import appModuleHandler
from scriptHandler import script
import ui
import api
import controlTypes
import config
import re
import time
import speech
import addonHandler
import wx
from speech.extensions import filter_speechSequence

addonHandler.initTranslation()

_CHAT_LIST_DUPLICATE_WINDOW = 0.25
_CONFIG_SECTION = "WhatsAppEnhancer"

from .text_window import TextWindow
from NVDAObjects.IAccessible.ia2Web import Ia2Web
from .wh_text import PHONE_RE, is_usage_hint, sender_label_size, strip_sender_phone, strip_usage_hint
from .wh_utils import collect_elements, find_element

class HeaderMenuDialog(Ia2Web):
	_v_idx = -1
	_items_cache = None

	def _get_items(self):
		if self._items_cache:
			return self._items_cache
		root = self
		try:
			while root and root.parent and root.role != controlTypes.Role.WINDOW:
				loc = root.location
				if loc and loc.width > 300 and loc.height > 300:
					break
				root = root.parent
		except Exception:
			pass

		items = []
		stack = [root]
		visited = 0
		while stack and visited < 300:
			o = stack.pop()
			visited += 1
			if o != root:
				is_target = o.role in (controlTypes.Role.BUTTON, controlTypes.Role.LISTITEM)
				if not is_target and o.role == controlTypes.Role.STATICTEXT and o.name and len(o.name.strip()) > 1:
					is_target = True

				if is_target:
					name = o.name
					if not name:
						sub = collect_elements(o, lambda x: x.name, max_items=10)
						name = " ".join([s.name for s in sub if s.name])
					if name and name.strip():
						items.append(o)
						continue

			try:
				child = o.lastChild
				while child:
					stack.append(child)
					child = child.previous
			except Exception:
				pass
		self._items_cache = items
		return self._items_cache

	def _announce(self, items):
		if not items or self._v_idx < 0:
			return
		obj = items[self._v_idx]
		name = obj.name
		if not name:
			sub = collect_elements(obj, lambda o: o.name, max_items=20)
			name = " ".join([s.name for s in sub if s.name])

		state_list = []
		for s_name in ("CHECKED", "SELECTED", "PRESSED", "ON"):
			s_val = getattr(controlTypes.State, s_name, None)
			if s_val and s_val in obj.states:
				state_list.append(controlTypes.stateLabels[s_val])

		full_msg = name or _("Option")
		if state_list:
			full_msg += f" ({', '.join(state_list)})"
		ui.message(full_msg)

	def script_next(self, gesture):
		items = self._get_items()
		if not items:
			return gesture.send()
		self._v_idx = (self._v_idx + 1) % len(items)
		self._announce(items)

	def script_prev(self, gesture):
		items = self._get_items()
		if not items:
			return gesture.send()
		self._v_idx = (self._v_idx - 1) % len(items)
		self._announce(items)

	def script_activate(self, gesture):
		items = self._get_items()
		if items and 0 <= self._v_idx < len(items):
			target = items[self._v_idx]
			try:
				target.doAction()
			except Exception:
				try:
					target.click()
				except Exception:
					gesture.send()
		else:
			gesture.send()

	def event_loseFocus(self):
		self._items_cache = None
		self._v_idx = -1

	__gestures = {
		"kb:downArrow": "next",
		"kb:upArrow": "prev",
		"kb:control+enter": "activate",
	}

class AppModule(appModuleHandler.AppModule):
	disableBrowseModeByDefault = True
	scriptCategory = _("WhatsApp Enhancer")

	_TIMESTAMP_RE = re.compile(r'^\d{1,2}[:.]\d{2}(\s*[AaPp][Mm])?$')

	def _is_ts(self, text):
		return bool(self._TIMESTAMP_RE.match(text.strip()))

	def _collect_leaf_texts(self, obj, depth=0):
		if depth > 8:
			return []
		results = []
		try:
			role = obj.role
			children = getattr(obj, "children", []) or []
			if role in (controlTypes.Role.STATICTEXT, controlTypes.Role.PANE):
				name = (getattr(obj, "name", "") or "").strip()
				if name and not children:
					results.append(name)
					return results
			for child in children:
				results.extend(self._collect_leaf_texts(child, depth + 1))
		except Exception:
			pass
		return results

	def _extract_message_body(self, obj):
		full_name = (getattr(obj, "name", "") or "").strip()
		leaves = self._collect_leaf_texts(obj)
		if leaves:
			filtered = [t for t in leaves if not self._is_ts(t) and not is_usage_hint(t)]
			if filtered:
				label_size = sender_label_size(filtered, self._is_ts)
				if label_size:
					filtered = filtered[label_size:]
				elif len(filtered) > 1 and (len(filtered[0]) < 40
					and full_name.startswith(filtered[0])
					and len(filtered[0]) < len(full_name) - 5):
					filtered = filtered[1:]
			if filtered:
				result = "\r\n".join(filtered)
				result = strip_usage_hint(result).strip()
				return result or None
		if not full_name:
			return None
		cleaned = strip_usage_hint(full_name).strip()
		cleaned = re.sub(r"\s*\d{1,2}[:.]\d{2}(\s*[AaPp][Mm])?\s*$", "", cleaned).strip()
		sender = next(
			(t for t in leaves
			 if t and len(t) < 40 and cleaned.startswith(t) and len(t) < len(cleaned) - 5),
			None
		)
		if sender is None:
			words = cleaned.split()
			if words:
				first = words[0]
				remainder = cleaned[len(first):].lstrip(" :")
				if (len(first) < 30
						and " " not in first
						and re.match(r'^[A-Za-z\u00C0-\u024F]+$', first)
						and len(remainder) > 40):
					sender = first

		if sender:
			cleaned = cleaned[len(sender):].lstrip(" :")
		return cleaned.strip() or None

	def _locate_collapsed(self, obj):
		try:
			if obj.role == controlTypes.Role.BUTTON:
				if controlTypes.State.COLLAPSED in getattr(obj, "states", set()):
					return obj
			for child in getattr(obj, "children", []) or []:
				found = self._locate_collapsed(child)
				if found:
					return found
		except Exception:
			pass
		return None

	def _gather_buttons_until(self, obj, stop_obj):
		if obj is stop_obj:
			return [], True
		btns = []
		if obj.role == controlTypes.Role.BUTTON:
			btns.append(obj)
		for child in getattr(obj, "children", []) or []:
			child_btns, found = self._gather_buttons_until(child, stop_obj)
			btns.extend(child_btns)
			if found:
				return btns, True
		return btns, False

	def _collect_message_texts(self, obj, min_len=15, depth=0):
		if depth > 9:
			return []
		texts = []
		try:
			role = obj.role
			children = getattr(obj, "children", []) or []
			if role in (controlTypes.Role.STATICTEXT, controlTypes.Role.PANE):
				name = (getattr(obj, "name", "") or "").strip()
				if name and len(name) >= min_len and not self._TIMESTAMP_RE.match(name):
					if not children:
						texts.append(name)
			val = (getattr(obj, "value", "") or "").strip()
			if val and len(val) >= min_len and not self._TIMESTAMP_RE.match(val):
				texts.append(val)
			for child in children:
				texts.extend(self._collect_message_texts(child, min_len, depth + 1))
		except Exception:
			pass
		return texts



	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.mainWindow = None
		self._last_spoken_text = ""
		self._last_spoken_lines = []
		self._review_cursor = 0
		self._review_line_index = 0
		self._is_reviewing = False
		self._focus_in_chat_list_table = False
		self._last_chat_list_speech = ("", 0.0)
		self._patch_speech()

	def _read_bool(self, key, default):
		try:
			val = config.conf[_CONFIG_SECTION].get(key, default)
			if isinstance(val, bool):
				return val
			return str(val).lower() not in ("false", "0", "")
		except Exception:
			return default

	def _has_message_list_ancestor(self, obj):
		current = obj
		for _ in range(7):
			try:
				cls = getattr(current, "IA2Attributes", {}).get("class", "")
				if "focusable-list-item" in cls:
					return True
				current = current.parent
				if current is None:
					return False
			except Exception:
				break
		return False

	def _is_chat_list_item(self, obj):
		try:
			parent = obj.parent
			if parent is None:
				return False
			if parent.role == controlTypes.Role.LIST:
				loc = parent.location
				if loc and loc.left < 450 and loc.width < 500:
					return True
			if parent.role == controlTypes.Role.LISTITEM:
				gp = parent.parent
				if gp and gp.role == controlTypes.Role.LIST:
					loc = gp.location
					if loc and loc.left < 450 and loc.width < 500:
						return True
		except Exception:
			pass
		return False

	def _is_in_chat_list_table(self, obj):
		for current in api.getFocusAncestors() + [obj]:
			try:
				attrs = getattr(current, "IA2Attributes", {})
				if current.role == controlTypes.Role.TABLE and attrs.get("xml-roles") == "grid":
					return True
			except Exception:
				continue
		return False

	def event_NVDAObject_init(self, obj):
		target_roles = {
			controlTypes.Role.SECTION,
			getattr(controlTypes.Role, "ROW", None),
			getattr(controlTypes.Role, "TABLECELL", None),
			getattr(controlTypes.Role, "GRIDCELL", None),
			getattr(controlTypes.Role, "CELL", None),
		}
		target_roles.discard(None)
		if obj.role in target_roles:
			obj.role = controlTypes.Role.PANE
			if hasattr(obj, "presType_layout"):
				try:
					obj.presentationType = obj.presType_layout
				except Exception:
					pass
		try:
			obj.rowNumber = None
			obj.columnNumber = None
		except Exception:
			pass

	def _apply_phone_filter(self, obj):
		name = obj.name
		if not name or len(name) < 10:
			return
		if '+' not in name:
			return
		in_message_list = self._has_message_list_ancestor(obj)
		if in_message_list:
			if self._read_bool("filter_phone_numbers_messages", True) and PHONE_RE.search(name):
				# Only containers have a sender label: a text object may be the message itself.
				if getattr(obj, "childCount", 0):
					filtered = strip_sender_phone(name, self._collect_leaf_texts(obj), self._is_ts)
					if filtered != name:
						obj.name = filtered
		else:
			if self._is_chat_list_item(obj):
				if self._read_bool("filter_phone_numbers_chat", False):
					filtered = PHONE_RE.sub('', name)
					if filtered != name:
						obj.name = re.sub(r'\s{2,}', ' ', filtered).strip()



	def event_gainFocus(self, obj, nextHandler):
		self._focus_in_chat_list_table = self._is_in_chat_list_table(obj)
		# Runs here and not in event_NVDAObject_init: walking the tree creates objects,
		# and each new object would run the filter again, freezing NVDA.
		try:
			self._apply_phone_filter(obj)
		except Exception:
			pass
		try:
			if not self.mainWindow or not self.mainWindow.windowHandle:
				curr = obj
				while curr:
					if curr.role == controlTypes.Role.WINDOW:
						self.mainWindow = curr
						break
					curr = curr.parent
		except Exception:
			pass
		try:
			if not self._read_bool("disable_browse_mode_lock", False):
				ti = getattr(obj, "treeInterceptor", None)
				if ti:
					ti.passThrough = True
		except Exception:
			pass
		nextHandler()

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		cls = getattr(obj, "IA2Attributes", {}).get("class", "")
		if "xyi3aci" in cls and "xe2zdcy" in cls:
			clsList.insert(0, HeaderMenuDialog)
		if "xuwfzo9" in cls and obj.parent:
			p = obj.parent
			p_cls = getattr(p, "IA2Attributes", {}).get("class", "")
			if "xyi3aci" in p_cls:
				clsList.insert(0, HeaderMenuDialog)

	def terminate(self):
		self._unpatch_speech()
		super().terminate()

	def _patch_speech(self):
		filter_speechSequence.register(self._filter_speech)

	def _unpatch_speech(self):
		filter_speechSequence.unregister(self._filter_speech)

	def _filter_speech(self, sequence):
		focus = api.getFocusObject()
		if not focus or getattr(focus, "appModule", None) is not self:
			return sequence
		new_sequence = []
		filter_hints = not self._read_bool("read_usage_hints", True)
		for item in sequence:
			if isinstance(item, str) and filter_hints:
				item = strip_usage_hint(item)
			new_sequence.append(item)
		text_list = [item for item in new_sequence if isinstance(item, str)]
		full_text = " ".join(text_list)
		if full_text.strip() and self._focus_in_chat_list_table:
			# ponytail: heuristic window; replace with event source IDs if NVDA exposes them.
			speech_key = " ".join(full_text.split())
			now = time.monotonic()
			last_key, last_time = self._last_chat_list_speech
			self._last_chat_list_speech = (speech_key, now)
			if speech_key == last_key and now - last_time < _CHAT_LIST_DUPLICATE_WINDOW:
				return []
		if not self._is_reviewing:
			if full_text.strip():
				self._last_spoken_text = full_text
				self._last_spoken_lines = [line for line in text_list if line.strip()]
				self._review_cursor = 0
				self._review_line_index = 0
		return new_sequence

	@script(description=_("Review previous character"), gesture="kb:NVDA+leftArrow")
	def script_review_previous_character(self, gesture):
		if not self._last_spoken_text: return
		self._is_reviewing = True
		try:
			if self._review_cursor > 0:
				self._review_cursor -= 1
			if self._review_cursor >= len(self._last_spoken_text):
				self._review_cursor = len(self._last_spoken_text) - 1
			speech.speak([self._last_spoken_text[self._review_cursor]])
		finally: self._is_reviewing = False

	@script(description=_("Review next character"), gesture="kb:NVDA+rightArrow")
	def script_review_next_character(self, gesture):
		if not self._last_spoken_text: return
		self._is_reviewing = True
		try:
			if self._review_cursor < len(self._last_spoken_text) - 1:
				self._review_cursor += 1
			elif self._review_cursor >= len(self._last_spoken_text):
				self._review_cursor = len(self._last_spoken_text) - 1
			speech.speak([self._last_spoken_text[self._review_cursor]])
		finally: self._is_reviewing = False

	@script(description=_("Review previous word"), gesture="kb:NVDA+control+leftArrow")
	def script_review_previous_word(self, gesture):
		if not self._last_spoken_text: return
		self._is_reviewing = True
		try:
			cur = self._review_cursor - 1
			while cur >= 0 and self._last_spoken_text[cur].isspace(): cur -= 1
			word_end = cur + 1
			while cur >= 0 and not self._last_spoken_text[cur].isspace(): cur -= 1
			self._review_cursor = max(0, cur + 1)
			speech.speak([self._last_spoken_text[self._review_cursor:word_end]])
		finally: self._is_reviewing = False

	@script(description=_("Review next word"), gesture="kb:NVDA+control+rightArrow")
	def script_review_next_word(self, gesture):
		if not self._last_spoken_text: return
		self._is_reviewing = True
		try:
			cur = self._review_cursor
			while cur < len(self._last_spoken_text) and not self._last_spoken_text[cur].isspace(): cur += 1
			while cur < len(self._last_spoken_text) and self._last_spoken_text[cur].isspace(): cur += 1
			self._review_cursor = cur
			word_end = cur
			while word_end < len(self._last_spoken_text) and not self._last_spoken_text[word_end].isspace(): word_end += 1
			speech.speak([self._last_spoken_text[self._review_cursor:word_end]])
		finally: self._is_reviewing = False

	@script(description=_("Review previous line"), gesture="kb:NVDA+upArrow")
	def script_review_previous_line(self, gesture):
		if not self._last_spoken_lines: return
		self._is_reviewing = True
		try:
			if self._review_line_index > 0: self._review_line_index -= 1
			speech.speak([self._last_spoken_lines[self._review_line_index]])
		finally: self._is_reviewing = False

	@script(description=_("Review next line"), gesture="kb:NVDA+downArrow")
	def script_review_next_line(self, gesture):
		if not self._last_spoken_lines: return
		self._is_reviewing = True
		try:
			if self._review_line_index < len(self._last_spoken_lines) - 1: self._review_line_index += 1
			speech.speak([self._last_spoken_lines[self._review_line_index]])
		finally: self._is_reviewing = False

	@script(description=_("Inspector"), gesture="kb:NVDA+shift+i")
	def script_inspector(self, gesture):
		obj = api.getFocusObject()
		loc = obj.location
		if loc:
			loc_str = _("L:{left}, T:{top}, W:{width}, H:{height}").format(
				left=loc.left, top=loc.top, width=loc.width, height=loc.height
			)
		else:
			loc_str = _("No Loc")
		auto_id = getattr(obj, "UIAAutomationId", "None")
		role_text = controlTypes.roleLabels.get(obj.role, obj.role)
		ui.message(_("Role: {role}, {loc_str}, Name: '{name}', ID: {auto_id}").format(
			role=role_text, loc_str=loc_str, name=obj.name, auto_id=auto_id
		))

	@script(description=_("Show / read complete message"), gesture="kb:alt+c")
	def script_show_text_message(self, gesture):
		obj = api.getFocusObject()
		if not self._has_message_list_ancestor(obj):
			gesture.send()
			return
		focus_name = (getattr(obj, "name", "") or "")
		if "…" not in focus_name:
			text = self._extract_message_body(obj)
			if text:
				TextWindow(text, _("Message Text"))
			else:
				gesture.send()
			return
		parent = getattr(obj, "parent", None)
		if not parent:
			text = self._extract_message_body(obj)
			if text:
				TextWindow(text, _("Message Text"))
			else:
				gesture.send()
			return
		siblings = getattr(parent, "children", []) or []
		all_parts = []
		for sib in siblings:
			all_parts.extend(self._collect_message_texts(sib))
		existing = " ".join(all_parts)
		if not existing:
			existing = focus_name
		if len(existing) > 800:
			TextWindow(existing, _("Message Text"))
			return
		for sib in siblings:
			collapsed_btn = self._locate_collapsed(sib)
			if not collapsed_btn:
				continue
			all_buttons, _found = self._gather_buttons_until(sib, collapsed_btn)
			focusable = [b for b in all_buttons if controlTypes.State.FOCUSABLE in getattr(b, "states", set())]
			if len(focusable) >= 2:
				read_more = focusable[1]
			elif len(focusable) == 1:
				read_more = focusable[0]
			else:
				continue
			read_more.doAction()
			msg_parent = parent
			def _show_expanded(p=msg_parent):
				try:
					speech.cancelSpeech()
				except Exception:
					pass
				parts = []
				try:
					for s in getattr(p, "children", []) or []:
						parts.extend(self._collect_message_texts(s))
				except Exception:
					pass
				full = "\r\n".join(parts) if parts else focus_name
				if full:
					TextWindow(full, _("Message Text"))
				else:
					ui.message(_("Text not found"))
			wx.CallLater(150, _show_expanded)
			return
		TextWindow(existing or focus_name, _("Message Text"))

	@script(description=_("Copy message"), gesture="kb:control+c")
	def script_copyMessage(self, gesture):
		obj = api.getFocusObject()
		if obj.role == controlTypes.Role.EDITABLETEXT:
			gesture.send()
			return
		if not self._has_message_list_ancestor(obj):
			gesture.send()
			return
		text = self._extract_message_body(obj)
		if text:
			api.copyToClip(text)
			ui.message(_("Copied"))
		else:
			gesture.send()

	@script(description=_("Context menu"), gesture="kb:shift+enter")
	def script_contextMenu(self, gesture):
		f = api.getFocusObject()
		if f.role == controlTypes.Role.EDITABLETEXT:
			gesture.send()
			return

		def is_context_button(obj):
			if obj.role != controlTypes.Role.BUTTON:
				return False
			states = getattr(obj, "states", set())
			is_popup = (controlTypes.State.COLLAPSED in states) or (controlTypes.State.EXPANDED in states)
			if not is_popup:
				name = (getattr(obj, "name", "") or "").lower()
				if name:
					for k in ("menu", "context", "opsi", "option", "bağlam", "контекст"):
						if k in name:
							return True
				return False
			cls = getattr(obj, "IA2Attributes", {}).get("class", "")
			if cls:
				classes = set(cls.split())
				if classes & {"_ahkm", "xmix8c7", "x1xp8n7a", "xbrszos", "xea3l6g", "xhslqc4", "x16dsc37", "x1jzctok", "x1bvqhpb", "x1ypdohk", "x1djpfga", "x1im30kd", "xtijo5x", "xs7f9wi"}:
					return True
			return False

		if is_context_button(f):
			try:
				f.doAction()
				return
			except Exception:
				pass

		container = f
		for _ in range(8):
			if not container or container.role == controlTypes.Role.WINDOW:
				break
			cls = getattr(container, "IA2Attributes", {}).get("class", "")
			if "focusable-list-item" in cls or container.role == controlTypes.Role.LISTITEM:
				break
			container = container.parent

		if not container:
			container = f

		btn = find_element(container, is_context_button, max_items=150)
		if btn:
			try:
				btn.doAction()
				return
			except Exception:
				pass

		gesture.send()

	@script(description=_("Play voice message"), gesture="kb:enter")
	def script_playVoiceMessage(self, gesture):
		f = api.getFocusObject()
		if f.role == controlTypes.Role.EDITABLETEXT:
			gesture.send()
			return
		
		def activate_button(obj):
			try:
				obj.doAction()
				return True
			except Exception:
				pass
			try:
				obj.click()
				return True
			except Exception:
				pass
			try:
				obj.setFocus()
				gesture.send()
				return True
			except Exception:
				return False

		def is_voice_play_button(obj):
			if obj.role != controlTypes.Role.BUTTON:
				return False
			attrs = getattr(obj, "IA2Attributes", {})
			cls = attrs.get("class", "")
			tag = attrs.get("tag", "")
			return (
				tag == "button"
				and "html-button" in cls
				and "xdj266r" in cls
				and "x14z9mp" in cls
			)

		def is_voice_message_context(obj):
			curr = obj
			for _ in range(5):
				if not curr:
					break
				cls = getattr(curr, "IA2Attributes", {}).get("class", "")
				if "focusable-list-item" in cls:
					return True
				curr = curr.parent
			return False

		if is_voice_play_button(f):
			activate_button(f)
			return

		if not is_voice_message_context(f):
			gesture.send()
			return

		container = f
		for _ in range(8):
			if not container or container.role == controlTypes.Role.WINDOW:
				break
			cls = getattr(container, "IA2Attributes", {}).get("class", "")
			if "focusable-list-item" in cls or container.role == controlTypes.Role.LISTITEM:
				break
			container = container.parent

		if not container:
			container = f

		btn = find_element(container, is_voice_play_button, max_items=150)
		if btn and activate_button(btn):
			return

		gesture.send()

	@script(description=_("Toggle browse mode"), gestures=["kb:NVDA+space"])
	def script_disableBrowseModeToggle(self, gesture):
		if self._read_bool("disable_browse_mode_lock", False):
			try:
				import globalCommands
				s = getattr(globalCommands.commands, "script_toggleVirtualBufferPassThrough", None)
				if s:
					s(gesture)
				else:
					gesture.send()
			except Exception:
				gesture.send()
			return
		try:
			obj = api.getFocusObject()
			ti = getattr(obj, "treeInterceptor", None)
			if ti:
				ti.passThrough = True
		except Exception:
			pass
		ui.message(_("Browse Mode is disabled for WhatsApp"))

	@script(description=_("Toggle phone number filtering in chat list"))
	def script_toggleChatListPhones(self, gesture):
		try:
			new_val = not self._read_bool("filter_phone_numbers_chat", False)
			config.conf[_CONFIG_SECTION]["filter_phone_numbers_chat"] = new_val
			config.conf.save()
			if new_val:
				ui.message(_("Chat list: phone numbers hidden"))
			else:
				ui.message(_("Chat list: phone numbers visible"))
		except Exception:
			pass

	@script(description=_("Toggle phone number filtering in message list"))
	def script_toggleMessageListPhones(self, gesture):
		try:
			new_val = not self._read_bool("filter_phone_numbers_messages", True)
			config.conf[_CONFIG_SECTION]["filter_phone_numbers_messages"] = new_val
			config.conf.save()
			if new_val:
				ui.message(_("Message list: phone numbers hidden"))
			else:
				ui.message(_("Message list: phone numbers visible"))
		except Exception:
			pass

