import sys
import os
import time
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK
from ahk.window import WindowNotFoundError
import pytest
import subprocess
ahk = AHK()

def test_get_calculator():
    p = None
    try:
        p = subprocess.Popen('notepad')
        time.sleep(1)  # give notepad time to start up
        win = ahk.win_get(title='Untitled - Notepad')
        assert win
        assert win.position
    finally:
        if p is not None:
            p.terminate()

def test_win_close():
    p = None
    try:
        p = subprocess.Popen('notepad')
        time.sleep(1)  # give notepad time to start up
        win = ahk.win_get(title='Untitled - Notepad')
        assert win
        assert win.position
        win.close()
        with pytest.raises(WindowNotFoundError):
            ahk.win_get(title='Untitled - Notepad').position
    finally:
        if p is not None:
            p.terminate()

def test_find_window_func():
    p = None
    try:
        p = subprocess.Popen('notepad')
        time.sleep(1)  # give notepad time to start up
        def func(win):
            return b'Untitled' in win.title
        win = ahk.find_window(title=b'Untitled - Notepad')
        assert win == ahk.find_window(func=func)
    finally:
        if p is not None:
            p.terminate()
