import subprocess
import time
from unittest import TestCase

from ahk import AHK


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
        self.assertFalse(self.win.exist)

        self.win.show()
        self.assertTrue(self.win.exist)

    def test_kill(self):
        self.win.kill()
        self.assertFalse(self.win.exist)

    def test_max_min(self):
        self.assertTrue(self.win.non_max_non_min)

        self.win.maximize()
        self.assertTrue(self.win.maximized)

        self.win.minimize()
        self.assertTrue(self.win.minimized)

        self.win.restore()
        self.assertTrue(self.win.maximized)

    def test_names(self):
        self.assertEqual(self.win.class_name, b'Notepad')
        self.assertEqual(self.win.title, b'Untitled - Notepad')
        self.assertEqual(self.win.text, b'')

    def tearDown(self):
        self.p.terminate()


if __name__ == "__main__":
    ahk = AHK()
    p = subprocess.Popen('notepad')
    time.sleep(1)
    win = ahk.win_get(title='Untitled - Notepad')
    print(win.transparent)
    win.transparent = 255
