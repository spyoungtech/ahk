import asyncio
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK, AsyncAHK
from unittest import TestCase, IsolatedAsyncioTestCase
from PIL import Image
from itertools import product
import time


class TestScreen(IsolatedAsyncioTestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AsyncAHK()
        self.before_windows = asyncio.run(self.ahk.windows())
        im = Image.new('RGB', (20, 20))
        for coord in product(range(20), range(20)):
            im.putpixel(coord, (255, 0, 0))
        self.im = im
        im.show()
        time.sleep(2)

    async def asyncTearDown(self):
        async for win in await self.ahk.windows():
            if win not in self.before_windows:
                await win.close()
                break

    def test_pixel_search(self):
        result = await self.ahk.pixel_search(0xFF0000)
        self.assertIsNotNone(result)

    def test_image_search(self):
        self.im.save('testimage.png')
        position = await self.ahk.image_search('testimage.png')
        self.assertIsNotNone(position)

    def test_pixel_get_color(self):
        x, y = await self.ahk.pixel_search(0xFF0000)
        result = await self.ahk.pixel_get_color(x, y)
        self.assertIsNotNone(result)
        self.assertEqual(int(result, 16), 0xFF0000)
