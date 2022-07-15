from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import AHK


class Window:
    def __init__(self, engine: AHK, ahk_id: str):
        self._engine: AHK = engine
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

class SyncControl:
    def __init__(self, window: Window, control_class: str):
        self.window: Window = window
        self.control_class: str = control_class
