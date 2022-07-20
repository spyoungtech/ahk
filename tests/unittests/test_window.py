import subprocess
import time
from unittest import TestCase
import os, sys

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)

from ahk import AHK
from ahk.daemon import AHKDaemon
from ahk.window import WindowNotFoundError


class TestWindow(TestCase):
    def setUp(self):
        self.ahk = AHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    def test_transparent(self):
        self.assertEqual(self.win.transparent, 255)

        self.win.transparent = 220
        self.assertEqual(self.win.transparent, 220)

        self.win.transparent = 255
        self.assertEqual(self.win.transparent, 255)

    def test_pinned(self):
        self.assertFalse(self.win.always_on_top)

        self.win.always_on_top = True
        self.assertTrue(self.win.always_on_top)

        self.win.always_on_top = False
        self.assertFalse(self.win.always_on_top)

    def test_close(self):
        self.win.close()
        self.assertFalse(self.win.exist)

    def test_show_hide(self):
        self.win.hide()
        time.sleep(0.5)
        self.assertFalse(self.win.exist)

        self.win.show()
        time.sleep(0.5)
        self.assertTrue(self.win.exist)

    def test_kill(self):
        self.win.kill()
        time.sleep(0.5)
        self.assertFalse(self.win.exist)

    def test_max_min(self):
        self.assertTrue(self.win.non_max_non_min)

        self.win.maximize()
        time.sleep(0.5)
        self.assertTrue(self.win.maximized)

        self.win.minimize()
        time.sleep(0.5)
        self.assertTrue(self.win.minimized)

        self.win.restore()
        time.sleep(0.5)
        self.assertTrue(self.win.maximized)

    def test_names(self):
        self.assertEqual(self.win.class_name, b'Notepad')
        self.assertEqual(self.win.title, b'Untitled - Notepad')
        self.assertEqual(self.win.text, b'')

    def test_height_change(self):
        current_height = self.win.height
        self.win.height = current_height + 100
        assert self.win.height == current_height + 100

    def test_width_change(self):
        current_width = self.win.width
        self.win.width = current_width + 100
        assert self.win.width == current_width + 100

    def test_rect_setter(self):
        """
        get rect ;-)
        """
        x, y, width, height = self.win.rect
        self.win.rect = (x + 10, y + 10, width + 10, height + 10)
        assert self.win.rect == (x + 10, y + 10, width + 10, height + 10)

    def test_title_change(self):
        self.win.title = 'foo'
        assert self.win.title == b'foo'

    def tearDown(self):
        self.p.terminate()

    def test_find_window(self):
        win = self.ahk.find_window(title=b'Untitled - Notepad')
        assert win.id == self.win.id

    def test_find_window_nonexistent_is_none(self):
        win = self.ahk.find_window(title=b'This should not exist')
        assert win is None

    def test_winget_nonexistent_window_is_none(self):
        win = self.ahk.win_get(title='This should not exist')
        assert win is None

    def test_winwait_nonexistent_raises_timeout_error(self):
        with pytest.raises(TimeoutError):
            win = self.ahk.win_wait(title='This should not exist')

    def test_winwait_existing_window(self):
        win = self.ahk.win_wait(title='Notepad')
        assert win.id == self.win.id

    def test_winwait_existing_window_with_exact(self):
        win = self.ahk.win_wait(title='Untitled - Notepad', exact=True)
        assert win.id == self.win.id


class TestWindowDaemon(TestWindow):
    def setUp(self):
        self.ahk = AHKDaemon()
        self.ahk.start()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    def tearDown(self):
        super().tearDown()
        self.ahk.stop()
