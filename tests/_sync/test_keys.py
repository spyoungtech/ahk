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
        self.ahk.set_capslock_state('Off')

    def tearDown(self) -> None:
        self.ahk.set_capslock_state('Off')
        try:
            self.p.kill()
        except Exception:
            pass
        self.ahk._transport._proc.kill()

    def test_set_capslock(self):
        self.ahk.set_capslock_state('On')
        assert self.ahk.key_state('CapsLock', mode='T') == 1
