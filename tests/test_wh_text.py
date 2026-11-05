"""Run from the repository root with: python -m pytest tests"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "addon", "appModules"))

from wh_text import is_phone_only, is_usage_hint, strip_sender_phone, strip_usage_hint  # noqa: E402


def is_time(text):
	return bool(re.match(r'^\d{1,2}[:.]\d{2}(\s*[AaPp][Mm])?$', text.strip()))


@pytest.mark.parametrize("text", [
	"Vou para minha casa agora",
	"Para mim tá ótimo",
	"Mandei para Maria ontem",
	"Para mais informações clique no link, ok?",
	"Para acessar o menu do restaurante, clique no link",
	"Tudo certo, ok. Para mais detalhes me liga amanhã",
	"Para más información llámame, ok",
	"Daha fazla para ver, ok",
	"Pour plus tard, ok",
	"Para mais opções me chama\nabri o menu ontem e vi outra coisa\nfim",
	"สำหรับคุณ",
	"更多的朋友",
])
def test_ordinary_text_is_kept(text):
	assert strip_usage_hint(text) == text
	assert not is_usage_hint(text)


@pytest.mark.parametrize("text, expected", [
	("Oi pessoal For more options, press left or right arrow", "Oi pessoal"),
	("Oi pessoal Para mais opções, pressione a seta para a direita", "Oi pessoal"),
	("Hola Para más opciones, pulsa la flecha derecha", "Hola"),
	("Selam Daha fazla seçenek için sağ ok tuşuna basın", "Selam"),
	("Hi Для получения меню", "Hi"),
])
def test_hint_is_removed_and_message_kept(text, expected):
	assert strip_usage_hint(text) == expected


def test_text_that_is_only_a_hint():
	assert is_usage_hint("Para mais opções, pressione a seta para a direita")


@pytest.mark.parametrize("text", ["+55 71 99999-9999", "‪+55 71 99999-9999‬", "+1 (415) 555-2671"])
def test_phone_only(text):
	assert is_phone_only(text)


@pytest.mark.parametrize("text", ["Meu número é +55 71 99999-9999", "+55 71", "10:32", ""])
def test_not_phone_only(text):
	assert not is_phone_only(text)


def test_sender_number_is_removed():
	name = "+55 71 99999-9999 Bom dia, pessoal 10:32"
	leaves = ["+55 71 99999-9999", "Bom dia, pessoal", "10:32"]
	assert strip_sender_phone(name, leaves, is_time) == "Bom dia, pessoal 10:32"


def test_profile_name_stays_and_number_goes():
	name = "Talvez Maria +55 71 9999-9999 Bom dia! 10:32 Mensagem lida"
	leaves = ["~", "Maria", "+55 71 9999-9999", "Bom dia!", "10:32"]
	assert strip_sender_phone(name, leaves, is_time) == "Talvez Maria Bom dia! 10:32 Mensagem lida"


def test_profile_name_with_emoji_that_is_not_in_the_text_objects():
	emoji = chr(0x1f60f)
	name = f"Talvez Maria{emoji} +55 71 9999-9999 Oi 10:32"
	leaves = ["~", "Maria", "+55 71 9999-9999", "Oi", "10:32"]
	assert strip_sender_phone(name, leaves, is_time) == f"Talvez Maria{emoji} Oi 10:32"


def test_message_starting_with_digits_keeps_them():
	name = "Talvez Maria +55 71 9999-9999 5 reais 10:32"
	leaves = ["~", "Maria", "+55 71 9999-9999", "5 reais", "10:32"]
	assert strip_sender_phone(name, leaves, is_time) == "Talvez Maria 5 reais 10:32"


def test_only_the_label_number_goes_when_the_message_repeats_it():
	name = "Talvez Maria +55 71 9999-9999 meu +55 71 9999-9999 10:32"
	leaves = ["~", "Maria", "+55 71 9999-9999", "meu +55 71 9999-9999", "10:32"]
	assert strip_sender_phone(name, leaves, is_time) == "Talvez Maria meu +55 71 9999-9999 10:32"


def test_real_portuguese_hint_keeps_the_status():
	hint = "Para acessar o menu e encontrar mais opções, pressione a tecla de seta para a esquerda ou direita"
	assert strip_usage_hint(f"Bom dia 10:32 Mensagem lida {hint}") == "Bom dia 10:32 Mensagem lida"
	assert is_usage_hint(hint)


def test_number_only_message_with_hint_is_kept():
	name = "+55 71 99999-9999 10:32"
	leaves = ["+55 71 99999-9999", "10:32", "Para mais opções, pressione a seta"]
	assert strip_sender_phone(name, leaves, is_time) == name


@pytest.mark.parametrize("name, leaves", [
	# Number typed in the middle of a message.
	("Meu número é +55 71 99999-9999 pode ligar 10:32", ["Meu número é +55 71 99999-9999 pode ligar", "10:32"]),
	# Message that starts with a number.
	("+55 71 99999-9999 é meu novo número 10:32", ["+55 71 99999-9999 é meu novo número", "10:32"]),
	# Message that is only a number: the time is the only other text.
	("+55 71 99999-9999 10:32", ["+55 71 99999-9999", "10:32"]),
	# Text object without children.
	("+55 71 99999-9999", ["+55 71 99999-9999"]),
	# Sender label is someone's name and the message has the number.
	("Maria +55 71 99999-9999 10:32", ["Maria", "+55 71 99999-9999", "10:32"]),
	# Saved contact who typed a number on the first line of a longer message.
	("Maria +55 71 99999-9999 me liga 10:32", ["Maria", "+55 71 99999-9999", "me liga", "10:32"]),
	# Sender outside the contacts who sent only a number.
	("Talvez Maria +55 71 9999-9999 10:32", ["~", "Maria", "+55 71 9999-9999", "10:32"]),
])
def test_typed_number_is_kept(name, leaves):
	assert strip_sender_phone(name, leaves, is_time) == name
