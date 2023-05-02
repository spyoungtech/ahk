import asyncio
import os
import subprocess
import sys
import time
from unittest import TestCase

from ahk import AHK
from ahk import Window


sleep = time.sleep


class TestMouseAsync(TestCase):
    win: Window

    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        try:
            self.ahk._transport._proc.kill()
        except:
            pass
        time.sleep(0.2)

    def test_mouse_position(self) -> None:
        pos = self.ahk.get_mouse_position()
        assert isinstance(pos, tuple)
        assert len(pos) == 2
        x, y = pos
        assert isinstance(x, int)
        assert isinstance(y, int)

    def test_mouse_move(self) -> None:
        self.ahk.mouse_move(x=100, y=100)
        pos = self.ahk.get_mouse_position()
        assert pos == (100, 100)
        self.ahk.mouse_move(x=200, y=200)
        pos2 = self.ahk.get_mouse_position()
        assert pos2 == (200, 200)

    def test_mouse_move_rel(self):
        self.ahk.mouse_move(x=100, y=100)
        sleep(0.5)
        pos = self.ahk.get_mouse_position()
        assert pos == (100, 100)
        self.ahk.mouse_move(x=10, y=10, relative=True)
        sleep(0.5)
        pos2 = self.ahk.get_mouse_position()
        x1, y1 = pos
        x2, y2 = pos2
        assert abs(x1 - x2) == 10
        assert abs(y1 - y2) == 10

    def test_mouse_move_nonblocking(self):
        self.ahk.mouse_move(100, 100)
        res = self.ahk.mouse_move(500, 500, speed=5, blocking=False)
        current_pos = self.ahk.get_mouse_position()
        sleep(0.1)
        pos = self.ahk.get_mouse_position()
        assert pos != current_pos
        assert pos != (500, 500)
        res.result()
