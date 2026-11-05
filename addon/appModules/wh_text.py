"""Text rules for usage hints and sender phone numbers.

Kept free of NVDA imports so the rules can be unit tested. When a rule is unsure,
it must keep the text: hearing a redundant hint or number is better than losing
part of a message.
"""
import re

_BIDI_CHARS = "".join(map(chr, (0x200e, 0x200f, *range(0x202a, 0x202f), *range(0x2066, 0x206a))))
_PHONE_CHARS = rf"()\d\s{_BIDI_CHARS}-"

PHONE_RE = re.compile(rf"\+\d[{_PHONE_CHARS}]{{11,}}")
_PHONE_ONLY_RE = re.compile(rf"^[{_BIDI_CHARS}\s]*\+\d[{_PHONE_CHARS}]{{11,}}$")

# How a hint starts. Common words such as "Para m" must not be used on their own:
# they also start ordinary sentences.
_HINT_LEAD = (
	r"For more options|Untuk opsi|Para lebih|Para más opciones|Para mais opções|Para acessar o menu e encontrar mais opções|Pour plus|Per lebih|"
	r"Per più|Für weitere|Daha fazla|Voor meer|Untuk mengakses|Untuk selengkapnya|"
	r"Untuk bantuan|Untuk mendapatkan|Для получения|"
	r"Để biết thêm|สำหรับตัวเลือก|"
	r"その他のオプション|更多选项|"
	r"अधिक विकल्पों|추가 옵션"
)
# The keyboard action a hint always mentions. "ok" alone means "arrow" only in Turkish,
# and only next to the word for "key"; elsewhere it is a very common word.
_HINT_ACTION = (
	r"arrow|panah|\bsetas?\b|flecha|flèche|freccia|pfeil|pijl|\bok tuş|"
	r"стрелк|mũi tên|ลูกศร|矢印|箭头|"
	r"तीर|화살표|menu|меню|メニュー|菜单|"
	r"मेनू|메뉴|konteks|context|contesto|contextuel|contestuale|kontext|bağlam|"
	r"контекст|ngữ cảnh|บริบท"
)
# A hint is always the end of the text, so nothing after it can be lost.
_HINT_RE = re.compile(rf"(?:{_HINT_LEAD})[^\n]*?(?:{_HINT_ACTION})[^\n]*\s*$", re.I)


def strip_usage_hint(text):
	"""Remove a usage hint from the end of text, keeping everything before it."""
	if not text:
		return text
	match = _HINT_RE.search(text)
	if not match:
		return text
	return text[:match.start()].rstrip()


def is_usage_hint(text):
	"""True when text has nothing but a usage hint."""
	return bool(text) and not strip_usage_hint(text.strip())


def is_phone_only(text):
	"""True when text has nothing but a phone number."""
	return bool(text) and bool(_PHONE_ONLY_RE.match(text.strip()))


def sender_label_size(leaves, is_timestamp):
	"""How many of the first texts of a message are its sender label.

	WhatsApp gives a sender outside the contacts as "~", the profile name and the number,
	in separate texts. Without "~", only a number alone in the first text can be a label.
	The message text must come after the label: otherwise the number is the message.
	"""
	if not leaves:
		return 0
	indexes = (1, 2) if leaves[0].strip() == "~" else (0,)
	for index in indexes:
		if index >= len(leaves) or not is_phone_only(leaves[index]):
			continue
		has_body = any(
			leaf.strip() and not is_timestamp(leaf) and not is_usage_hint(leaf)
			for leaf in leaves[index + 1:]
		)
		return index + 1 if has_body else 0
	return 0


def strip_sender_phone(name, leaves, is_timestamp):
	"""Remove the sender's number from the accessible name of a message container.

	The profile name stays. Numbers that people typed in the message are kept.
	"""
	if not name:
		return name
	size = sender_label_size(leaves, is_timestamp)
	if not size:
		return name
	phone = leaves[size - 1].strip(_BIDI_CHARS + " ")
	position = name.find(phone)
	if position < 0:
		return name
	# Without "~", the number has to open the text to be a label.
	if size == 1 and name[:position].strip(_BIDI_CHARS + " "):
		return name
	result = name[:position] + " " + name[position + len(phone):]
	return re.sub(r"\s{2,}", " ", result).strip()
