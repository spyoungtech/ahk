import asyncio
import time
import unittest.mock

from ahk import AHK


sleep = time.sleep


class TestWindowAsync(unittest.TestCase):
    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_clipboard(self):
        self.ahk.set_clipboard('foo')
        contents = self.ahk.get_clipboard()
        assert contents == 'foo'

    def test_clipboard_all(self):
        self.ahk.set_clipboard('Hello \N{EARTH GLOBE AMERICAS}')
        data = self.ahk.get_clipboard_all()
        self.ahk.set_clipboard('foo')
        assert data != self.ahk.get_clipboard_all()
        self.ahk.set_clipboard_all(data)
        assert data == self.ahk.get_clipboard_all()
        assert self.ahk.get_clipboard() == 'Hello \N{EARTH GLOBE AMERICAS}'

    def test_on_clipboard_change(self):
        with unittest.mock.MagicMock(return_value=None) as m:
            self.ahk.on_clipboard_change(m)
            self.ahk.start_hotkeys()
            self.ahk.set_clipboard('foo')
            self.ahk.set_clipboard('bar')
            sleep(1)
            m.assert_called()
