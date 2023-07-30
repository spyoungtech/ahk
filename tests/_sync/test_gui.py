import asyncio
import time
import unittest

import pytest

from ahk import AHK


sleep = time.sleep


class TestGui(unittest.TestCase):
    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_msg_box(self):
        box = self.ahk.msg_box(text='hello', title='test', timeout=3, blocking=False)
        sleep(1)
        win = self.ahk.win_get(title='test')
        assert win is not None
        with pytest.raises(TimeoutError):
            r = box.result()
