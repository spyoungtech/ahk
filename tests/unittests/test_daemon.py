import asyncio
import subprocess
import time
import sys
import os
from unittest import TestCase
from itertools import product


project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk.daemon import AHKDaemon
from ahk.window import Window, WindowNotFoundError
from PIL import Image
from ahk.keys import KEYS



class TestKeyboardDaemon(TestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AHKDaemon()
        self.ahk.start()
        self.before_windows = self.ahk.windows()
        self.p = subprocess.Popen("notepad")
        time.sleep(1)
        self.notepad = self.ahk.find_window(title=b"Untitled - Notepad")

    def tearDown(self):
        self.ahk.stop()
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

    def test_send_input(self):
        self.notepad.activate()
        self.ahk.send_input("Hello World")
        time.sleep(0.5)
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

    def test_set_capslock_state(self):
        self.ahk.set_capslock_state("on")
        assert self.ahk.key_state("CapsLock", "T")

class TestMouseDaemon(TestCase):
    def setUp(self) -> None:
        self.ahk = AHKDaemon()
        self.ahk.start()

    def test_mouse_move(self):
        x, y = self.ahk.mouse_position
        self.ahk.mouse_move(10, 10, relative=True)
        assert self.ahk.mouse_position == (x+10, y+10)

    def tearDown(self) -> None:
        self.ahk.stop()

class TestScreen(TestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AHKDaemon()
        self.ahk.start()
        self.before_windows = self.ahk.windows()
        im = Image.new('RGB', (20, 20))
        for coord in product(range(20), range(20)):
            im.putpixel(coord, (255, 0, 0))
        self.im = im
        im.show()
        time.sleep(2)

    def tearDown(self):
        for win in self.ahk.windows():
            if win not in self.before_windows:
                win.close()
                break
        self.ahk.stop()

    def test_pixel_search(self):
        result = self.ahk.pixel_search(0xFF0000)
        self.assertIsNotNone(result)

    def test_image_search(self):
        self.im.save('testimage.png')
        position = self.ahk.image_search('testimage.png')
        self.assertIsNotNone(position)

    def test_pixel_get_color(self):
        x, y = self.ahk.pixel_search(0xFF0000)
        result = self.ahk.pixel_get_color(x, y)
        self.assertIsNotNone(result)
        self.assertEqual(int(result, 16), 0xFF0000)
