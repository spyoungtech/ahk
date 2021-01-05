import subprocess
import time
from unittest import TestCase
import asyncio
import os
import sys
project_root = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
)
sys.path.insert(0, project_root)
from ahk import AHK, AsyncAHK
from ahk.window import AsyncWindow


class TestWindowAsync(TestCase):
    win: AsyncWindow
    def setUp(self):
        self.ahk = AsyncAHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = asyncio.run(self.ahk.win_get(title='Untitled - Notepad'))
        self.assertIsNotNone(self.win)

    async def a_transparent(self):
        self.assertEqual(await self.win.get_transparency(), 255)

        self.win.transparent = 220
        self.assertEqual(await self.win.get_transparency(), 220)

        self.win.transparent = 255
        self.assertEqual(await self.win.transparent, 255)


    def test_transparent(self):
        asyncio.run(self.a_transparent())
#
    def test_pinned(self):
        asyncio.run(self.a_pinned())
    async def a_pinned(self):
        self.assertFalse(await self.win.always_on_top)

        await self.win.set_always_on_top(True)
        self.assertTrue(await self.win.is_always_on_top())

        self.win.always_on_top = False
        await asyncio.sleep(1)
        self.assertFalse(await self.win.always_on_top)

    async def a_close(self):
        await self.win.close()
        await asyncio.sleep(0.2)
        self.assertFalse(await self.win.exists())
        self.assertFalse(await self.win.exist)

    def test_close(self):
        asyncio.run(self.a_close())

    async def a_show_hide(self):
        await self.win.hide()
        await asyncio.sleep(0.5)
        self.assertFalse(await self.win.exist)

        await self.win.show()
        await asyncio.sleep(0.5)
        self.assertTrue(await self.win.exist)

    def test_show_hide(self):
        asyncio.run(self.a_show_hide())

    async def a_kill(self):
        await self.win.kill()
        await asyncio.sleep(0.5)
        self.assertFalse(await self.win.exist)

    def test_kill(self):
        asyncio.run(self.a_kill())

    async def a_max_min(self):
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
    def test_max_min(self):
        asyncio.run(self.a_max_min())
#
    async def a_names(self):
        self.assertEqual(await self.win.class_name, b'Notepad')
        self.assertEqual(await self.win.get_class_name(), b'Notepad')

        self.assertEqual(await self.win.title, b'Untitled - Notepad')
        self.assertEqual(await self.win.get_title(), b'Untitled - Notepad')

        self.assertEqual(await self.win.text, b'')
        self.assertEqual(await self.win.get_text(), b'')


    def test_names(self):
        asyncio.run(self.a_names())
#
    def tearDown(self):
        self.p.terminate()
