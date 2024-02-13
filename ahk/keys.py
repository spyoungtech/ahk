from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Final
from typing import List
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing import Union


class Key:
    is_modifier: bool = False
    symbol: str = ''

    def __init__(self, key_name: str):
        self._key_name: str = key_name

    @property
    def name(self) -> str:
        return self._key_name

    @property
    def DOWN(self) -> str:
        return '{' + f'{self.name} down' + '}'

    @property
    def UP(self) -> str:
        return '{' + f'{self.name} up' + '}'

    def __str__(self) -> str:
        return '{' + self.name + '}'

    def __hash__(self) -> int:
        return hash(str(self))

    def __mul__(self, n: int) -> str:
        if not isinstance(n, int):
            return NotImplemented
        return '{' + f'{self.name} {n}' + '}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Key) or isinstance(other, str):
            return NotImplemented
        return hash(self) == hash(other)

    def __add__(self, s: str) -> str:
        return str(self) + s

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(key_name={self.name!r})'

    def __format__(self, format_spec: Any) -> str:
        return str(self)


SYMBOLS: Dict[str, str]
SYMBOLS = {
    'Win': '#',
    'LWin': '<#',
    'RWin': '>#',
    'Shift': '+',
    'LShift': '<+',
    'RShift': '>+',
    'Alt': '!',
    'LAlt': '<!',
    'RAlt': '>!',
    'Control': '^',
    'LControl': '<^',
    'RControl': '>^',
}


class KeyCombo:
    def __init__(self, *modifiers: KeyModifier):
        self._s: Optional[str] = None
        self.modifiers: List[KeyModifier] = list(modifiers)
        assert all([isinstance(key, KeyModifier) for key in self.modifiers]), 'Keys must be modifiers'

    def __str__(self) -> str:
        s = ''.join(mod.symbol for mod in self.modifiers)
        if self._s is not None:
            s += self._s
        return s

    def __add__(self, other: object) -> Any:
        if (
            not isinstance(other, KeyCombo)
            and not isinstance(other, KeyModifier)
            and not isinstance(other, Key)
            and not isinstance(other, str)
        ):
            return NotImplemented
        if self._s is not None:
            raise ValueError('Key combo is already terminated')
        if isinstance(other, KeyCombo):
            combo = KeyCombo(*[*self.modifiers, *other.modifiers])
            if other._s:
                combo = combo + other._s
            return combo
        if isinstance(other, KeyModifier):
            self.modifiers.append(other)  # XXX: ????
        elif isinstance(other, Key) or isinstance(other, str):
            self._s = str(other)
            return self

    def __repr__(self) -> str:
        key_modifiers = ', '.join(repr(mod) for mod in self.modifiers)
        return f'{self.__class__.__name__}({key_modifiers}){f"+{self._s!r}" if self._s else f""}'


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


class KeyModifier(Key):
    is_modifier = True

    @property
    def symbol(self) -> str:  # type: ignore[override]
        return SYMBOLS.get(self.name, str(self))

    def __add__(self, other: object) -> Any:
        if isinstance(other, KeyModifier):
            return KeyCombo(self, other)
        elif isinstance(other, KeyCombo):
            return other + self

        if not isinstance(other, Stringable):
            return NotImplemented

        return self.symbol + str(other)


class KEYS:
    """
    KEYS constants
    REF: https://autohotkey.com/docs/KeyList.htm
    """

    CAPS_LOCK: Final[Key] = Key('CapsLock')
    CapsLock: Final[Key] = CAPS_LOCK
    SCROLL_LOCK: Final[Key] = Key('ScrollLock')
    ScrollLock: Final[Key] = SCROLL_LOCK
    SPACE: Final[Key] = Key('Space')
    TAB: Final[Key] = Key('Tab')
    Tab: Final[Key] = TAB
    ENTER: Final[Key] = Key('Enter')
    Enter: Final[Key] = ENTER
    ESCAPE: Final[Key] = Key('Escape')
    BACKSPACE: Final[Key] = Key('Backspace')
    Backspace: Final[Key] = BACKSPACE
    UP: Final[Key] = Key('Up')
    Up: Final[Key] = UP
    DOWN: Final[Key] = Key('Down')
    Down: Final[Key] = DOWN
    LEFT: Final[Key] = Key('Left')
    Left: Final[Key] = LEFT
    RIGHT: Final[Key] = Key('Right')
    Right: Final[Key] = RIGHT
    DELETE: Final[Key] = Key('Delete')
    DEL: Final[Key] = DELETE
    Delete: Final[Key] = DELETE
    Del: Final[Key] = DELETE
    WIN: Final[KeyModifier] = KeyModifier('Win')
    Win: Final[Key] = WIN
    LEFT_WIN: Final[KeyModifier] = KeyModifier('LWin')
    LWin: Final[Key] = LEFT_WIN
    RIGHT_WIN: Final[KeyModifier] = KeyModifier('RWin')
    RWin: Final[Key] = RIGHT_WIN
    CONTROL: Final[KeyModifier] = KeyModifier('Control')
    Control: Final[Key] = CONTROL
    CTRL: Final[Key] = CONTROL
    Ctrl: Final[Key] = CONTROL
    LEFT_CONTROL: Final[KeyModifier] = KeyModifier('LControl')
    LCtrl: Final[Key] = LEFT_CONTROL
    LControl: Final[Key] = LEFT_CONTROL
    RIGHT_CONTROL: Final[KeyModifier] = KeyModifier('RControl')
    RCtrl: Final[Key] = RIGHT_CONTROL
    RControl: Final[Key] = RIGHT_CONTROL
    ALT: Final[KeyModifier] = KeyModifier('Alt')
    Alt: Final[Key] = ALT
    LEFT_ALT: Final[KeyModifier] = KeyModifier('LAlt')
    LAlt: Final[Key] = LEFT_ALT
    RIGHT_ALT: Final[KeyModifier] = KeyModifier('RAlt')
    RAlt: Final[Key] = RIGHT_ALT
    SHIFT: Final[KeyModifier] = KeyModifier('Shift')
    Shift: Final[Key] = SHIFT
    LEFT_SHIFT: Final[KeyModifier] = KeyModifier('LShift')
    LShift: Final[Key] = LEFT_SHIFT
    RIGHT_SHIFT: Final[KeyModifier] = KeyModifier('RShift')
    RShift: Final[Key] = RIGHT_SHIFT
    NUMPAD_DOT: Final[Key] = Key('NumpadDot')
    NumpadDot: Final[Key] = NUMPAD_DOT
    NUMPAD_DEL: Final[Key] = Key('NumpadDel')
    NumpadDel: Final[Key] = NUMPAD_DEL
    NUM_LOCK: Final[Key] = Key('NumLock')
    NumLock: Final[Key] = NUM_LOCK
    NUMPAD_ADD: Final[Key] = Key('NumpadAdd')
    NUMPAD_DIV: Final[Key] = Key('NumpadDiv')
    NUMPAD_SUB: Final[Key] = Key('NumpadSub')
    NUMPAD_MULT: Final[Key] = Key('NumpadMult')
    NUMPAD_ENTER: Final[Key] = Key('NumpadEnter')
    NumpadAdd: Final[Key] = NUMPAD_ADD
    NumpadDiv: Final[Key] = NUMPAD_DIV
    NumpadSub: Final[Key] = NUMPAD_SUB
    NumpadMult: Final[Key] = NUMPAD_MULT
    NumpadEnter: Final[Key] = NUMPAD_ENTER


def _init_keys() -> None:
    '''put this in a function to avoid polluting global namespace'''
    for i in range(0, 10):
        #  set numpad keys
        key_name = f'Numpad{i}'
        key = Key(key_name)
        setattr(KEYS, key_name, key)
        setattr(KEYS, key_name.upper(), key)

    for i in range(1, 25):
        # set function keys
        key_name = f'F{i}'
        setattr(KEYS, key_name, Key(key_name))

    for i in range(1, 33):
        # set joystick keys
        key_name = f'Joy{i}'
        setattr(KEYS, key_name, Key(key_name))
        setattr(KEYS, key_name.upper(), Key(key_name))


_init_keys()

__all__ = [name for name in dir(KEYS) if not name.startswith('_')]


def __getattr__(name: str) -> Union[Key, KeyModifier]:
    obj = getattr(KEYS, name, None)
    if not isinstance(obj, Key) and not isinstance(obj, KeyModifier):
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    return obj
