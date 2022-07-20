import subprocess
import time
from unittest import IsolatedAsyncioTestCase
import asyncio
import os
import sys

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK, AsyncAHK
from ahk.window import AsyncWindow


class TestWindowAsync(IsolatedAsyncioTestCase):
    win: AsyncWindow

    def setUp(self):
        self.ahk = AsyncAHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = asyncio.run(self.ahk.win_get(title='Untitled - Notepad'))
        self.assertIsNotNone(self.win)

    async def a_transparent(self):
        self.assertEqual(await self.win.get_transparency(), 255)

        await self.win.set_transparency(220)
        self.assertEqual(await self.win.get_transparency(), 220)

        self.win.transparent = 255
        await asyncio.sleep(0.5)
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

    async def test_find_window(self):
        win = await self.ahk.find_window(title=b'Untitled - Notepad')
        assert win.id == self.win.id

    async def test_find_window_nonexistent_is_none(self):
        win = await self.ahk.find_window(title=b'This should not exist')
        assert win is None

    async def test_winget_nonexistent_window_is_none(self):
        win = await self.ahk.win_get(title='This should not exist')
        assert win is None

    async def test_winwait_nonexistent_raises_timeout_error(self):
        with pytest.raises(TimeoutError):
            win = await self.ahk.win_wait(title='This should not exist')

    async def test_winwait_existing_window(self):
        win = await self.ahk.win_wait(title='Notepad')
        assert win.id == self.win.id

    async def test_winwait_existing_window_with_exact(self):
        win = await self.ahk.win_wait(title='Untitled - Notepad', exact=True)
        assert win.id == self.win.id

    def tearDown(self):
        self.p.terminate()
        asyncio.run(asyncio.sleep(0.5))
