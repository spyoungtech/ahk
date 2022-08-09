import asyncio
import os
import subprocess
import sys
import time
from unittest import IsolatedAsyncioTestCase

from ahk import AsyncAHK
from ahk import AsyncWindow

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep


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
        await async_sleep(0.5)
        pos = await self.ahk.get_mouse_position()
        assert pos == (100, 100)
        await self.ahk.mouse_move(x=10, y=10, relative=True)
        await async_sleep(0.5)
        pos2 = await self.ahk.get_mouse_position()
        x1, y1 = pos
        x2, y2 = pos2
        assert abs(x1 - x2) == 10
        assert abs(y1 - y2) == 10

    async def test_mouse_move_nonblocking(self):
        await self.ahk.mouse_move(100, 100)
        res = await self.ahk.mouse_move(500, 500, speed=5, blocking=False)
        current_pos = await self.ahk.get_mouse_position()
        await async_sleep(0.1)
        pos = await self.ahk.get_mouse_position()
        assert pos != current_pos
        assert pos != (500, 500)
        await res.result()
