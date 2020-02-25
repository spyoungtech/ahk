from unittest import TestCase, main
import subprocess
import time
from ahk import AHK


class TestWindow(TestCase):

    def setUp(self):
        self.ahk = AHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

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
        self.win.maximize()
        self.assertTrue(self.win.maximized)

        self.win.minimize()
        self.assertTrue(self.win.minimized)

        self.win.restore()
        self.assertTrue(self.win.maximized)

    def tearDown(self):
        self.p.terminate()
