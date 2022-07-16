import time
from itertools import product
from unittest import IsolatedAsyncioTestCase

from PIL import Image

from ahk import AsyncAHK


class TestScreen(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()
        self.before_windows = await self.ahk.list_windows()
        im = Image.new('RGB', (20, 20))
        for coord in product(range(20), range(20)):
            im.putpixel(coord, (255, 0, 0))
        self.im = im
        im.show()
        time.sleep(2)

    async def asyncTearDown(self):
        for win in await self.ahk.list_windows():
            if win not in self.before_windows:
                await win.close()
                break
        self.ahk._transport._proc.kill()

    #
    # async def test_pixel_search(self):
    #     result = await self.ahk.pixel_search(0xFF0000)
    #     self.assertIsNotNone(result)

    async def test_image_search(self):
        self.im.save('testimage.png')
        position = await self.ahk.image_search('testimage.png')
        assert isinstance(position, tuple)

    # async def test_pixel_get_color(self):
    #     x, y = await self.ahk.pixel_search(0xFF0000)
    #     result = await self.ahk.pixel_get_color(x, y)
    #     self.assertIsNotNone(result)
    #     self.assertEqual(int(result, 16), 0xFF0000)
