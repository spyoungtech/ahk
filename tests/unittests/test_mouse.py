import inspect
import os
import subprocess
import sys
import threading
import time
import asyncio
from itertools import product
from functools import partial
from unittest import TestCase, IsolatedAsyncioTestCase
project_root = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
)
sys.path.insert(0, project_root)
from ahk import AsyncAHK, AHK




class TestMouse(TestCase):
    def setUp(self) -> None:
        self.ahk = AHK()
        self.original_position = self.ahk.mouse_position
        self.notepad_process = None

    def tearDown(self) -> None:
        self.ahk.mouse_move(*self.original_position)
        if self.notepad_process is not None:
            self.notepad_process.terminate()

    def test_mouse_move(self):
        x, y = self.ahk.mouse_position
        self.ahk.mouse_move(10, 10, relative=True)
        assert self.ahk.mouse_position == (x+10, y+10)

    def test_mouse_move_absolute(self):
        original_x, original_y = self.original_position
        new_x = original_x + 10
        new_y = original_y + 10
        self.ahk.mouse_move(new_x, new_y)
        assert self.ahk.mouse_position == (new_x, new_y)

    def test_mouse_move_callable_speed(self):
        x, y = self.ahk.mouse_position
        self.ahk.mouse_move(10, 10, relative=True, speed=lambda: 10)
        assert self.ahk.mouse_position == (x+10, y+10)

    def test_mouse_drag(self):
        self.notepad_process = subprocess.Popen('notepad')
        notepad = self.ahk.find_window(title=b"Untitled - Notepad")
        win_width = notepad.width
        win_height = notepad.height
        self.ahk.mouse_move(*notepad.position)
        # moving the mouse to the window position puts it in a position where it can be resized by dragging ↖ ↘
        # after this, we expect the window height/width to shrink by 10px
        self.ahk.mouse_drag(10, 10, relative=True)
        assert notepad.width == win_width - 10
        assert notepad.height == win_height - 10


class TestMouseAsync(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.ahk = AsyncAHK()

    async def test_mouse_move(self):
        x, y = await self.ahk.mouse_position
        await self.ahk.mouse_move(10, 10, relative=True)
        assert await self.ahk.mouse_position == (x+10, y+10)


