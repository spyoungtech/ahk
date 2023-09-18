import asyncio
import subprocess
import time
from unittest import mock
from unittest import TestCase

from ahk import AHK
from ahk import Window


sleep = time.sleep


class TestHotkeysAsync(TestCase):
    win: Window

    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        self.ahk.stop_hotkeys()
        self.ahk._transport._proc.kill()
        subprocess.run(['TASKKILL', '/F', '/IM', 'AutoHotkey.exe'], capture_output=True)
        time.sleep(0.2)

    def test_hotkey(self):
        with mock.MagicMock(return_value=None) as m:
            self.ahk.add_hotkey('a', callback=m)
            self.ahk.start_hotkeys()
            self.ahk.key_down('a')
            self.ahk.key_press('a')
            sleep(1)
            m.assert_called()

    def test_hotkey_ex_handler(self):
        def side_effect():
            raise Exception('oh no')

        with mock.MagicMock() as mock_cb, mock.MagicMock() as mock_ex_handler:
            mock_cb.side_effect = side_effect
            self.ahk.add_hotkey('a', callback=mock_cb, ex_handler=mock_ex_handler)
            self.ahk.start_hotkeys()
            self.ahk.key_down('a')
            self.ahk.key_press('a')
            sleep(1)
            mock_ex_handler.assert_called()

    def test_remove_hotkey(self):
        with mock.MagicMock(return_value=None) as m:
            self.ahk.add_hotkey('a', callback=m)
            self.ahk.start_hotkeys()
            self.ahk.remove_hotkey('a')
            self.ahk.key_down('a')
            self.ahk.key_press('a')
            sleep(1)
            m.assert_not_called()

    def test_clear_hotkeys(self):
        with mock.MagicMock(return_value=None) as m:
            self.ahk.add_hotkey('a', callback=m)
            self.ahk.start_hotkeys()
            self.ahk.clear_hotkeys()
            self.ahk.key_down('a')
            self.ahk.key_press('a')
            sleep(1)
            m.assert_not_called()


class TestHotkeysAsyncV2(TestHotkeysAsync):
    def setUp(self) -> None:
        self.ahk = AHK(version='v2')
