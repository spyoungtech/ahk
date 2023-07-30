import enum

HOTKEY_ESCAPE_SEQUENCE_MAP = {
    '\n': '`n',
    '\t': '`t',
    '\r': '`r',
    '\a': '`a',
    '\b': '`b',
    '\f': '`f',
    '\v': '`v',
    ',': '`,',
    '%': '`%',
    '`': '``',
    ';': '`;',
    ':': '`:',
}

ESCAPE_SEQUENCE_MAP = {
    '!': '{!}',
    '^': '{^}',
    '+': '{+}',
    '{': '{{}',
    '}': '{}}',
    '#': '{#}',
    '=': '{=}',
}

_TRANSLATION_TABLE = str.maketrans(ESCAPE_SEQUENCE_MAP)

_HOTKEY_TRANSLATION_TABLE = str.maketrans(HOTKEY_ESCAPE_SEQUENCE_MAP)


def hotkey_escape(s: str) -> str:
    return s.translate(_HOTKEY_TRANSLATION_TABLE)


def type_escape(s: str) -> str:
    return s.translate(_TRANSLATION_TABLE)


class MsgBoxButtons(enum.IntEnum):
    OK = 0
    OK_CANCEL = 1
    ABORT_RETRY_IGNORE = 2
    YES_NO_CANCEL = 3
    YES_NO = 4
    RETRY_CANCEL = 5
    CANCEL_TRYAGAIN_CONTINUE = 6


class MsgBoxIcon(enum.IntEnum):
    HAND = 16
    QUESTION = 32
    EXCLAMATION = 48
    ASTERISK = 64


class MsgBoxDefaultButton(enum.IntEnum):
    SECOND = 256
    THIRD = 512
    FOURTH = 768


class MsgBoxModality(enum.IntEnum):
    SYSTEM_MODAL = 4096
    TASK_MODAL = 8192
    ALWAYS_ON_TOP = 262144


class MsgBoxOtherOptions(enum.IntEnum):
    HELP_BUTTON = 16384
    TEXT_RIGHT_JUSTIFIED = 524288
    RIGHT_TO_LEFT_READING_ORDER = 1048576
