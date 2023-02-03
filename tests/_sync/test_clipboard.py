import time
from unittest import TestCase

from ahk import AHK


class TestWindowAsync(TestCase):
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
