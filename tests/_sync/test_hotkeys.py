import asyncio
import subprocess
import time
from unittest import mock
from unittest import TestCase

from ahk import AHK
from ahk import Window


sleep = time.sleep


class TestMouseAsync(TestCase):
    win: Window

    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        self.ahk.stop_hotkeys()
        self.ahk._transport._proc.kill()
        subprocess.run(['TASKKILL', '/F', '/IM', 'AutoHotkey.exe'])

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
