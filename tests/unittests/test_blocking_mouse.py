import time
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK

ahk = AHK()


def test_blocking_blocks():
    ahk.mouse_position = (100, 100)
    assert ahk.mouse_position == (100, 100)
    ahk.mouse_move(10, 10, speed=30)
    assert ahk.mouse_position == (10, 10)


def test_nonblocking_does_not_block():
    ahk.mouse_position = (100, 100)
    assert ahk.mouse_position == (100, 100)
    ahk.mouse_move(10, 10, speed=30, blocking=False)
    assert ahk.mouse_position != (10, 10)
    time.sleep(0.1)
    assert ahk.mouse_position != (100, 100)  # make sure it actually moved!

