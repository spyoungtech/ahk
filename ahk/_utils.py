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
