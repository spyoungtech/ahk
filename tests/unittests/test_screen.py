import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK
from unittest import TestCase
from PIL import Image
from itertools import product
import time
from ahk.daemon import AHKDaemon


class TestScreen(TestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AHK()
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


class TestScreenDaemon(TestScreen):
    def setUp(self):
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
        super().tearDown()
        self.ahk.stop()
