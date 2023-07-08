import asyncio
import os
import subprocess
import sys
import time
import unittest.mock

from ahk import AHK
from ahk import Window


sleep = time.sleep


class TestWindowAsync(unittest.TestCase):
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
        self.p.communicate()
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_set_capslock(self):
        self.ahk.set_capslock_state('On')
        assert self.ahk.key_state('CapsLock', mode='T') == 1

    def test_hotstring(self):
        self.ahk.add_hotstring('btw', 'by the way')
        self.ahk.start_hotkeys()
        self.ahk.set_send_level(1)
        self.win.activate()
        self.ahk.send('btw ')
        time.sleep(2)

        assert 'by the way' in self.win.get_text()

    def test_remove_hotstring(self):
        self.ahk.add_hotstring('btw', 'by the way')
        self.ahk.start_hotkeys()
        self.ahk.set_send_level(1)
        self.win.activate()
        self.ahk.remove_hotstring('btw')
        self.ahk.send('btw ')
        time.sleep(2)
        assert 'by the way' not in self.win.get_text()

    def test_clear_hotstrings(self):
        self.ahk.add_hotstring('btw', 'by the way')
        self.ahk.start_hotkeys()
        self.ahk.set_send_level(1)
        self.win.activate()
        self.ahk.clear_hotstrings()
        self.ahk.send('btw ')
        time.sleep(2)
        assert 'by the way' not in self.win.get_text()

    def test_hotstring_callback(self):
        with unittest.mock.MagicMock(return_value=None) as m:
            self.ahk.add_hotstring('btw', m)
            self.ahk.start_hotkeys()
            self.ahk.set_send_level(1)
            self.win.activate()
            self.ahk.send('btw ')
            sleep(1)
            m.assert_called()
