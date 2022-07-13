from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import AHK


class Window:
    def __init__(self, engine: AHK, ahk_id: str):
        self._engine: AHK = engine
        self._ahk_id: str = ahk_id
