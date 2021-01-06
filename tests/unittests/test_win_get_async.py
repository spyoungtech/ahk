import asyncio
import sys
import os
import time
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK, AsyncAHK
from ahk.window import WindowNotFoundError
import pytest
import subprocess
from unittest import IsolatedAsyncioTestCase

class TestWinGetAsync(IsolatedAsyncioTestCase):
    def setUp(self):
        self.ahk = AsyncAHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = asyncio.run(self.ahk.win_get(title='Untitled - Notepad'))
        self.assertIsNotNone(self.win)

    def tearDown(self):
        self.p.terminate()
        asyncio.run(asyncio.sleep(0.5))


    async def test_get_calculator(self):
        assert await self.win.position

    async def a_win_get(self):
        win = await self.ahk.win_get(title='Untitled - Notepad')
        await win.position

    def test_win_close(self):
        asyncio.run(self.win.close())
        self.assertRaises(WindowNotFoundError, asyncio.run, self.a_win_get())

    async def test_find_window_func(self):
        async def func(win):
            return b'Untitled' in await win.title
        assert self.win == await self.ahk.find_window(func=func)

    async def test_getattr_window_subcommand(self):
        assert isinstance(await self.win.pid, str)
