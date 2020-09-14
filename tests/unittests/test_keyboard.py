import os
import subprocess
import sys
import threading
import time
from itertools import product
from unittest import TestCase

from ahk import AHK
from ahk.keys import ALT, CTRL, KEYS

project_root = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
)
sys.path.insert(0, project_root)


class TestKeyboard(TestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AHK()
        self.before_windows = self.ahk.windows()
        self.p = subprocess.Popen("notepad")
        time.sleep(1)
        self.notepad = self.ahk.find_window(title=b"Untitled - Notepad")

    def tearDown(self):
        self.p.terminate()
        time.sleep(0.2)

    def test_window_send(self):
        self.notepad.send("hello world")
        time.sleep(1)
        self.assertIn(b"hello world", self.notepad.text)

    def test_send(self):
        self.notepad.activate()
        self.ahk.send("hello world")
        assert b"hello world" in self.notepad.text

    def test_send_key_mult(self):
        self.notepad.send(KEYS.TAB * 4)
        time.sleep(0.5)
        self.assertEqual(self.notepad.text.count(b"\t"), 4, self.notepad.text)

    def test_send_input(self):
        self.notepad.activate()
        self.ahk.send_input("Hello World")
        assert b"Hello World" in self.notepad.text

    def test_type(self):
        self.notepad.activate()
        self.ahk.type("Hello, World!")
        assert b"Hello, World!" in self.notepad.text

    def test_type_escapes_equals(self):
        """
        https://github.com/spyoungtech/ahk/issues/96
        """
        self.notepad.activate()
        self.ahk.type("=foo")
        assert b"=foo" in self.notepad.text

    def test_sendraw_equals(self):
        """
        https://github.com/spyoungtech/ahk/issues/96
        """
        self.notepad.activate()
        self.ahk.send_raw("=foo")
        assert b"=foo" in self.notepad.text

    # def test_set_capslock_state(self):
    #     self.ahk.set_capslock_state("on")
    #     assert self.ahk.key_state("CapsLock", "T")


def a_down():
    time.sleep(0.5)
    ahk = AHK()
    ahk.key_down("a")


def release_a():
    time.sleep(0.5)
    ahk = AHK()
    ahk.key_up("a")


def press_a():
    time.sleep(0.5)
    ahk = AHK()
    ahk.key_press("a")


class TestKeys(TestCase):
    def setUp(self):
        self.ahk = AHK()
        self.thread = None
        self.hotkey = None

    def tearDown(self):
        if self.thread is not None:
            self.thread.join(timeout=3)
        if self.ahk.key_state("a"):
            self.ahk.key_up("a")
        if self.ahk.key_down("Control"):
            self.ahk.key_up("Control")

        notepad = self.ahk.find_window(title=b"Untitled - Notepad")
        if notepad:
            notepad.close()

        if self.hotkey and self.hotkey.running:
            self.hotkey.stop()

    def test_key_wait_pressed(self):
        start = time.time()
        self.thread = threading.Thread(target=a_down)
        self.thread.start()
        self.ahk.key_wait("a", timeout=5)
        end = time.time()
        assert end - start < 5

    def test_key_wait_released(self):
        start = time.time()
        a_down()
        self.thread = threading.Thread(target=release_a)
        self.thread.start()
        self.ahk.key_wait("a", timeout=2)

    def test_key_wait_timeout(self):
        self.assertRaises(TimeoutError, self.ahk.key_wait, "f", timeout=1)

    def test_key_state_when_not_pressed(self):
        self.assertFalse(self.ahk.key_state("a"))

    def test_key_state_pressed(self):
        self.ahk.key_down("Control")
        self.assertTrue(self.ahk.key_state("Control"))

    def test_hotkey(self):
        self.hotkey = self.ahk.hotkey(hotkey="a", script="Run Notepad")
        self.thread = threading.Thread(target=a_down)
        self.thread.start()
        self.hotkey.start()
        time.sleep(1)
        self.assertIsNotNone(self.ahk.find_window(title=b"Untitled - Notepad"))

    def test_hotkey_stop(self):
        self.hotkey = self.ahk.hotkey(hotkey="a", script="Run Notepad")
        self.hotkey.start()
        assert self.hotkey.running
        self.hotkey.stop()
        self.ahk.key_press("a")
        self.assertIsNone(self.ahk.find_window(title=b"Untitled - Notepad"))
