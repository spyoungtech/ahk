import asyncio
import os
import subprocess
import sys
import time
import tracemalloc
from unittest import TestCase

tracemalloc.start()

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

    def tearDown(self) -> None:
        try:
            self.p.kill()
        except:
            pass
        self.p.communicate()
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_exists(self):
        self.assertTrue(self.ahk.win_exists(title='Untitled - Notepad'))
        self.assertTrue(self.win.exists())

    def test_close(self):
        self.win.close()
        time.sleep(0.2)
        self.assertFalse(self.win.exists())

    def test_win_get_returns_none_nonexistent(self):
        win = self.ahk.win_get(title='DOES NOT EXIST')
        assert win is None

    def test_exists_nonexistent_is_false(self):
        assert self.ahk.win_exists(title='DOES NOT EXIST') is False

    def test_win_pid(self):
        pid = self.win.get_pid()
        assert isinstance(pid, int)

    def test_win_process_name(self):
        process_name = self.win.get_process_name()
        assert process_name == 'notepad.exe'

    def test_win_process_path(self):
        process_path = self.win.get_process_path()
        assert 'notepad.exe' in process_path

    def test_win_minmax(self):
        minmax = self.win.get_minmax()
        assert minmax == 0

    def test_win_set_always_on_top(self):
        assert self.win.is_always_on_top() is False
        self.win.set_always_on_top('On')
        assert self.win.is_always_on_top() is True

    def test_window_list_controls(self):
        controls = self.win.list_controls()
        assert isinstance(controls, list)
        assert len(controls) == 2

    def test_set_detect_hidden_windows(self):
        non_hidden = self.ahk.list_windows()
        self.ahk.set_detect_hidden_windows(True)
        all_windows = self.ahk.list_windows()
        assert len(all_windows) > len(non_hidden)

    def test_list_windows_hidden(self):
        non_hidden = self.ahk.list_windows()
        all_windows = self.ahk.list_windows(detect_hidden_windows=True)
        assert len(all_windows) > len(non_hidden)

    def test_win_get_title(self):
        title = self.win.get_title()
        assert title == 'Untitled - Notepad'

    def test_win_get_idlast(self):
        self.ahk.win_set_bottom(title='Untitled - Notepad')
        w = self.ahk.win_get_idlast(title='Untitled - Notepad')
        assert w == self.win

    def test_win_get_count(self):
        count = self.ahk.win_get_count(title='Untitled - Notepad')
        assert count == 1

    # async def test_win_get_count_hidden(self):
    #     count = await self.ahk.win_get_count()
    #     all_count = await self.ahk.win_get_count(detect_hidden_windows=True)
    #     assert all_count > count

    def test_win_exists(self):
        assert self.win.exists()
        self.win.close()
        assert not self.win.exists()

    def test_win_set_title(self):
        self.win.set_title(new_title='Foo')
        assert self.win.get_title() == 'Foo'

    def test_control_send_window(self):
        self.win.send('Hello World')
        text = self.win.get_text()
        assert 'Hello World' in text

    def test_send_literal_comma(self):
        self.win.send('hello, world')
        print(self.win)
        text = self.win.get_text()
        assert 'hello, world' in text

    def test_send_literal_tilde_n(self):
        expected_text = '```nim\nimport std/strformat\n```'
        self.win.send(expected_text)
        text = self.win.get_text()
        assert '```nim' in text
        assert '\nimport std/strformat' in text
        assert '\n```' in text

    def test_set_title_match_mode_and_speed(self):
        self.ahk.set_title_match_mode(('RegEx', 'Slow'))
        speed = self.ahk.get_title_match_speed()
        mode = self.ahk.get_title_match_mode()
        assert mode == 'RegEx'
        assert speed == 'Slow'

    def test_set_title_match_mode(self):
        self.ahk.set_title_match_mode('RegEx')
        mode = self.ahk.get_title_match_mode()
        assert mode == 'RegEx'

    def test_set_title_match_speed(self):
        self.ahk.set_title_match_mode('Slow')
        speed = self.ahk.get_title_match_speed()
        assert speed == 'Slow'

    def test_control_send_from_control(self):
        controls = self.win.list_controls()
        edit_control = controls[0]
        edit_control.send('hello world')
        text = self.win.get_text()
        assert 'hello world' in text

    def test_control_position(self):
        controls = self.win.list_controls()
        edit_control = controls[0]
        pos = edit_control.get_position()
        assert pos

    def test_win_position(self):
        pos = self.win.get_position()
        assert pos

    def test_win_activate(self):
        self.win.activate()
        w = self.ahk.get_active_window()
        assert w == self.win

    def test_win_get_class(self):
        assert self.win.get_class() == 'Notepad'
