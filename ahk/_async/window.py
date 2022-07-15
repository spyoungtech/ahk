from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import AsyncAHK


class AsyncWindow:
    def __init__(self, engine: AsyncAHK, ahk_id: str):
        self._engine: AsyncAHK = engine
        self._ahk_id: str = ahk_id

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__} ahk_id={self._ahk_id}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncWindow):
            return NotImplemented
        return self._ahk_id == other._ahk_id

    def __hash__(self) -> int:
        return hash(self._ahk_id)

    async def close(self) -> None:
        await self._engine.win_close(title=f'ahk_id {self._ahk_id}')
        return None


class AsyncControl:
    def __init__(self, window: AsyncWindow, control_class: str):
        self.window: AsyncWindow = window
        self.control_class: str = control_class
