import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK
from unittest import TestCase
from itertools import product
import time, subprocess
from ahk.keys import KEYS, ALT, CTRL


class TestKeyboard(TestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AHK()
        self.before_windows = self.ahk.windows()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.notepad = self.ahk.find_window(title=b'Untitled - Notepad')

    def tearDown(self):
        self.p.terminate()
        time.sleep(0.2)

    def test_window_send(self):
        self.notepad.send('hello world')
        time.sleep(1)
        self.assertIn(b'hello world', self.notepad.text)

    def test_send(self):
        self.notepad.activate()
        self.ahk.send('hello world')
        assert b'hello world' in self.notepad.text

    def test_send_key_mult(self):
        self.notepad.send(KEYS.TAB * 4)
        time.sleep(0.5)
        self.assertEqual(self.notepad.text.count(b'\t'), 4, self.notepad.text)

    def test_send_input(self):
        self.notepad.activate()
        self.ahk.send_input('Hello World')
        assert b'Hello World' in self.notepad.text

    def test_type(self):
        self.notepad.activate()
        self.ahk.type('Hello, World!')
        assert b'Hello, World!' in self.notepad.text
