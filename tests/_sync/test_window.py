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
