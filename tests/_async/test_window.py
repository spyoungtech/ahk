import asyncio
import os
import subprocess
import sys
import time
from unittest import IsolatedAsyncioTestCase

from ahk import AsyncAHK
from ahk import AsyncWindow


class TestWindowAsync(IsolatedAsyncioTestCase):
    win: AsyncWindow

    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = await self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    async def asyncTearDown(self) -> None:
        try:
            await self.win.close()
        except Exception:
            pass
        self.ahk._transport._proc.kill()

    async def test_exists(self):
        self.assertTrue(await self.ahk.win_exists(title='Untitled - Notepad'))
        self.assertTrue(await self.win.exists())

    async def test_close(self):
        await self.win.close()
        await asyncio.sleep(0.2)
        self.assertFalse(await self.win.exists())

    async def test_win_get_returns_none_nonexistent(self):
        win = await self.ahk.win_get(title='DOES NOT EXIST')
        assert win is None

    async def test_exists_nonexistent_is_false(self):
        assert await self.ahk.win_exists(title='DOES NOT EXIST') is False

    async def test_win_pid(self):
        pid = await self.win.get_pid()
        assert isinstance(pid, int)

    async def test_win_process_name(self):
        process_name = await self.win.get_process_name()
        assert process_name == 'notepad.exe'

    async def test_win_process_path(self):
        process_path = await self.win.get_process_path()
        assert 'notepad.exe' in process_path

    async def test_win_minmax(self):
        minmax = await self.win.get_minmax()
        assert minmax == 0

    async def test_win_set_always_on_top(self):
        assert await self.win.is_always_on_top() is False
        await self.win.set_always_on_top('On')
        assert await self.win.is_always_on_top() is True

    async def test_window_list_controls(self):
        controls = await self.win.list_controls()
        assert isinstance(controls, list)
        assert len(controls) == 2

    async def test_set_detect_hidden_windows(self):
        non_hidden = await self.ahk.list_windows()
        await self.ahk.set_detect_hidden_windows(True)
        all_windows = await self.ahk.list_windows()
        assert len(all_windows) > len(non_hidden)

    async def list_windows_hidden(self):
        non_hidden = await self.ahk.list_windows()
        all_windows = await self.ahk.list_windows(detect_hidden_windows=True)
        assert len(all_windows) > len(non_hidden)
