import asyncio
import time
import sys
import os
from unittest import IsolatedAsyncioTestCase

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk.daemon import AHKDaemon


class TestMouseAsync(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AHKDaemon()
        await self.ahk.start()

    def tearDown(self) -> None:
        self.ahk.stop()

    async def test_mouse_move(self):
        x, y = await self.ahk.mouse_position
        await self.ahk.mouse_move(10, 10, relative=True)
        assert await self.ahk.mouse_position == (x+10, y+10)



