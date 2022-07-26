import asyncio
import os
import subprocess
import sys
import time
from unittest import TestCase

from ahk import AHK
from ahk import Window


class TestWindowAsync(TestCase):
    win: Window

    def setUp(self) -> None:
        self.ahk = AHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    def tearDown(self) -> None:
        try:
            self.win.close()
        except Exception:
            pass
        self.ahk._transport._proc.kill()

    def test_exists(self):
        self.assertTrue(self.ahk.win_exists(title='Untitled - Notepad'))
        self.assertTrue(self.win.exists())

    def test_close(self):
        self.win.close()
        asyncio.sleep(0.2)
        self.assertFalse(self.win.exists())

    def test_win_get_returns_none_nonexistent(self):
        win = self.ahk.win_get(title='DOES NOT EXIST')
        assert win is None

    def test_exists_nonexistent_is_false(self):
        assert self.ahk.win_exists(title='DOES NOT EXIST') is False

    def test_win_pid(self):
        pid = self.win.get_pid()
        assert isinstance(pid, int)

    def test_win_process_name(self):
        process_name = self.win.get_process_name()
        assert process_name == 'notepad.exe'

    def test_win_process_path(self):
        process_path = self.win.get_process_path()
        assert 'notepad.exe' in process_path

    def test_win_minmax(self):
        minmax = self.win.get_minmax()
        assert minmax == 0

    def test_win_set_always_on_top(self):
        assert self.win.is_always_on_top() is False
        self.win.set_always_on_top('On')
        assert self.win.is_always_on_top() is True

    def test_window_list_controls(self):
        controls = self.win.list_controls()
        assert isinstance(controls, list)
        assert len(controls) == 2
