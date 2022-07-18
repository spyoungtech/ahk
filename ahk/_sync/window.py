from __future__ import annotations

from typing import Literal
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from .engine import AHK


class WindowNotFoundException(Exception):
    ...


class Window:
    def __init__(self, engine: AHK, ahk_id: str):
        self._engine: AHK = engine
        if not ahk_id:
            raise ValueError(f'Invalid ahk_id: {ahk_id!r}')
        self._ahk_id: str = ahk_id

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__} ahk_id={self._ahk_id}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Window):
            return NotImplemented
        return self._ahk_id == other._ahk_id

    def __hash__(self) -> int:
        return hash(self._ahk_id)

    def close(self) -> None:
        self._engine.win_close(title=f'ahk_id {self._ahk_id}')
        return None

    def exists(self) -> bool:
        return self._engine.win_exists(title=f'ahk_id {self._ahk_id}')

    def get_pid(self) -> int:
        pid = self._engine.win_get_pid(title=f'ahk_id {self._ahk_id}')
        if pid is None:
            raise WindowNotFoundException(
                f'Error when trying to get PID of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return pid

    def get_process_name(self) -> str:
        name = self._engine.win_get_process_name(title=f'ahk_id {self._ahk_id}')
        if name is None:
            raise WindowNotFoundException(
                f'Error when trying to get process name of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return name

    def get_process_path(self) -> str:
        path = self._engine.win_get_process_path(title=f'ahk_id {self._ahk_id}')
        if path is None:
            raise WindowNotFoundException(
                f'Error when trying to get process path of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return path

    def get_minmax(self) -> Union[Literal[0], Literal[1], Literal[-1]]:
        minmax = self._engine.win_get_minmax(title=f'ahk_id {self._ahk_id}')
        if minmax is None:
            raise WindowNotFoundException(
                f'Error when trying to get minmax state of window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return minmax


class SyncControl:
    def __init__(self, window: Window, hwnd: str, control_class: str):
        self.window: Window = window
        self.hwnd: str = hwnd
        self.control_class: str = control_class

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} window={self.window!r}, control_hwnd={self.hwnd!r}, control_class={self.control_class!r}>'
