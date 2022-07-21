import asyncio
import os
import subprocess
import sys
import time
from unittest import IsolatedAsyncioTestCase

from ahk import AsyncAHK
from ahk import AsyncWindow


class TestMouseAsync(IsolatedAsyncioTestCase):
    win: AsyncWindow

    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()

    async def test_mouse_position(self) -> None:
        pos = await self.ahk.get_mouse_position()
        assert isinstance(pos, tuple)
        assert len(pos) == 2
        x, y = pos
        assert isinstance(x, int)
        assert isinstance(y, int)

    async def test_mouse_move(self) -> None:
        await self.ahk.mouse_move(x=100, y=100)
        pos = await self.ahk.get_mouse_position()
        assert pos == (100, 100)
        await self.ahk.mouse_move(x=200, y=200)
        pos2 = await self.ahk.get_mouse_position()
        assert pos2 == (200, 200)

    async def test_mouse_move_rel(self):
        await self.ahk.mouse_move(x=100, y=100)
        pos = await self.ahk.get_mouse_position()
        assert pos == (100, 100)
        await self.ahk.mouse_move(x=10, y=10, relative=True)
        await asyncio.sleep(1)
        pos2 = await self.ahk.get_mouse_position()
        x1, y1 = pos
        x2, y2 = pos2
        await asyncio.sleep(1)
        assert abs(x1 - x2) == 10
        assert abs(y1 - y2) == 10
