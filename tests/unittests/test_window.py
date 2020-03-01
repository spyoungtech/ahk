import time
from unittest import TestCase

from ahk import AHK
from ahk.window import Window


class TestWindow(TestCase):

    def setUp(self):
        self.ahk = AHK()
        self.win = self.ahk.run_window("notepad")
        self.assertIsInstance(self.win, Window)

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

    def tearDown(self):
        self.win.close()
        self.assertFalse(self.win.exist)


if __name__ == "__main__":
    import logging
    import coloredlogs

    coloredlogs.install(level='DEBUG')
    logger = logging.getLogger(__name__)

    ahk = AHK()
    win = ahk.run("notepad")
    win.close()
    print(win)
