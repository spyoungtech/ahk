from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import AsyncAHK


class AsyncWindow:
    def __init__(self, engine: AsyncAHK, ahk_id: str):
        self._engine: AsyncAHK = engine
        self._ahk_id: str = ahk_id
