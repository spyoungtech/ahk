import asyncio
import subprocess
import time
import sys
import os
from unittest import IsolatedAsyncioTestCase
from itertools import product

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk.daemon import AsyncAHKDaemon
from ahk.window import AsyncWindow, WindowNotFoundError
from PIL import Image


class TestMouseDaemonAsync(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHKDaemon()
        await self.ahk.start()

    def tearDown(self) -> None:
        self.ahk.stop()

    async def test_mouse_move(self):
        x, y = await self.ahk.mouse_position
        await self.ahk.mouse_move(10, 10, relative=True)
        assert await self.ahk.mouse_position == (x + 10, y + 10)


class TestWindowDaemonAsync(IsolatedAsyncioTestCase):
    win: AsyncWindow

    async def asyncSetUp(self):
        self.ahk = AsyncAHKDaemon()
        await self.ahk.start()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = await self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    async def test_transparent(self):
        self.assertEqual(await self.win.get_transparency(), 255)

        await self.win.set_transparency(220)
        self.assertEqual(await self.win.get_transparency(), 220)

        self.win.transparent = 255
        await asyncio.sleep(0.5)
        self.assertEqual(await self.win.transparent, 255)

    async def test_pinned(self):
        self.assertFalse(await self.win.always_on_top)

        await self.win.set_always_on_top(True)
        self.assertTrue(await self.win.is_always_on_top())

        self.win.always_on_top = False
        await asyncio.sleep(1)
        self.assertFalse(await self.win.always_on_top)

    async def test_close(self):
        await self.win.close()
        await asyncio.sleep(0.2)
        self.assertFalse(await self.win.exists())
        self.assertFalse(await self.win.exist)

    async def test_show_hide(self):
        await self.win.hide()
        await asyncio.sleep(0.5)
        self.assertFalse(await self.win.exist)

        await self.win.show()
        await asyncio.sleep(0.5)
        self.assertTrue(await self.win.exist)

    async def test_kill(self):
        await self.win.kill()
        await asyncio.sleep(0.5)
        self.assertFalse(await self.win.exist)

    async def test_max_min(self):
        self.assertTrue(await self.win.non_max_non_min)
        self.assertFalse(await self.win.is_minmax())

        await self.win.maximize()
        await asyncio.sleep(1)
        self.assertTrue(await self.win.maximized)
        self.assertTrue(await self.win.is_maximized())

        await self.win.minimize()
        await asyncio.sleep(1)
        self.assertTrue(await self.win.minimized)
        self.assertTrue(await self.win.is_minimized())

        await self.win.restore()
        await asyncio.sleep(0.5)
        self.assertTrue(await self.win.maximized)
        self.assertTrue(await self.win.is_maximized())

    #
    async def test_names(self):
        self.assertEqual(await self.win.class_name, b'Notepad')
        self.assertEqual(await self.win.get_class_name(), b'Notepad')

        self.assertEqual(await self.win.title, b'Untitled - Notepad')
        self.assertEqual(await self.win.get_title(), b'Untitled - Notepad')

        self.assertEqual(await self.win.text, b'')
        self.assertEqual(await self.win.get_text(), b'')

    async def test_title_setter(self):
        starting_title = await self.win.title
        await self.win.set_title('new title')
        assert await self.win.get_title() != starting_title

    async def asyncTearDown(self):
        self.ahk.stop()
        self.p.terminate()
        await asyncio.sleep(0.5)


class TestScreenDaemonAsync(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AsyncAHKDaemon()
        await self.ahk.start()
        self.before_windows = await self.ahk.windows()
        im = Image.new('RGB', (20, 20))
        for coord in product(range(20), range(20)):
            im.putpixel(coord, (255, 0, 0))
        self.im = im
        im.show()
        time.sleep(2)

    async def asyncTearDown(self):
        for win in await self.ahk.windows():
            if win not in self.before_windows:
                await win.close()
                break
        self.ahk.stop()

    async def test_pixel_search(self):
        result = await self.ahk.pixel_search(0xFF0000)
        self.assertIsNotNone(result)

    async def test_image_search(self):
        self.im.save('testimage.png')
        position = await self.ahk.image_search('testimage.png')
        self.assertIsNotNone(position)

    async def test_pixel_get_color(self):
        x, y = await self.ahk.pixel_search(0xFF0000)
        result = await self.ahk.pixel_get_color(x, y)
        self.assertIsNotNone(result)
        self.assertEqual(int(result, 16), 0xFF0000)


class TestWinGetDaemonAsync(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.ahk = AsyncAHKDaemon()
        await self.ahk.start()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = await self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)

    async def asyncTearDown(self):
        self.p.terminate()
        await asyncio.sleep(0.5)
        self.ahk.stop()

    async def test_get_calculator(self):
        assert await self.win.position

    async def test_win_close(self):
        await self.win.close()
        win = await self.ahk.win_get(title='Untitled - Notepad')
        assert win is None

    async def test_find_window_func(self):
        async def func(win):
            return b'Untitled' in await win.title

        assert self.win == await self.ahk.find_window(func=func)

    async def test_getattr_window_subcommand(self):
        assert isinstance(await self.win.pid, str)


class TestKeyboardDaemonAsync(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AsyncAHKDaemon()
        await self.ahk.start()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)

    async def asyncTearDown(self):
        self.p.terminate()
        self.ahk.stop()
        await asyncio.sleep(0.5)

    async def test_window_send(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.send('hello world')
        await asyncio.sleep(1)
        self.assertIn(b'hello world', await notepad.get_text())

    async def test_send(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.activate()
        await self.ahk.send('hello world')
        self.assertIn(b'hello world', await notepad.get_text())

    async def test_send_input(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await self.ahk.send_input('Hello World')
        await asyncio.sleep(0.5)
        assert b'Hello World' in await notepad.get_text()

    async def test_type(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.activate()
        await self.ahk.type('Hello, World!')
        assert b'Hello, World!' in await notepad.get_text()

    async def test_multi_line_response(self):
        """
        Test that responses with multi-line strings are not truncated
        Not really a 'keyboard' test, but whatever
        """
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.activate()
        await self.ahk.type('Hello\nWorld!')
        text = await notepad.get_text()
        assert b'Hello\r\n' in text
        assert b'World!' in text
