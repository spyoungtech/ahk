import os
import subprocess
import sys
import threading
import time
import asyncio
from itertools import product
from unittest import TestCase, IsolatedAsyncioTestCase
project_root = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
)
sys.path.insert(0, project_root)
from ahk import AsyncAHK, AHK

class TestMouse(TestCase):
    def setUp(self) -> None:
        self.ahk = AHK()

    def test_mouse_move(self):
        x, y = self.ahk.mouse_position
        self.ahk.mouse_move(10, 10, relative=True)
        assert self.ahk.mouse_position == (x+10, y+10)

class TestMouseAsync(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.ahk = AsyncAHK()

    async def test_mouse_move(self):
        x, y = await self.ahk.mouse_position
        await self.ahk.mouse_move(10, 10, relative=True)
        assert await self.ahk.mouse_position == (x+10, y+10)


