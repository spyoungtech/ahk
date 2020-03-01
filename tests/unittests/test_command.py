from unittest import TestCase

from ahk import AHK
from ahk.window import Window


class TestCommand(TestCase):

    def setUp(self):
        self.ahk = AHK()

    def test_run(self):
        pid = self.ahk.run("notepad")
        self.assertNotIsInstance(pid, Window)

    def test_run_window(self):
        self.win = self.ahk.run_window("notepad")
        self.assertIsInstance(self.win, Window)

    def tearDown(self):
        win = self.ahk.find_window(title=b"Untitled - Notepad")
        win.close()
