import asyncio
import os
import subprocess
import sys
import time
import unittest.mock

from ahk import AsyncAHK
from ahk import AsyncWindow

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep


class TestKeysAsync(unittest.IsolatedAsyncioTestCase):
    win: AsyncWindow

    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = await self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)
        await self.ahk.set_capslock_state('Off')

    async def asyncTearDown(self) -> None:
        await self.ahk.set_capslock_state('Off')
        try:
            self.p.kill()
        except Exception:
            pass
        self.p.communicate()
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_set_capslock(self):
        await self.ahk.set_capslock_state('On')
        assert await self.ahk.key_state('CapsLock', mode='T') == 1

    async def test_hotstring(self):
        self.ahk.add_hotstring('btw', 'by the way')
        self.ahk.start_hotkeys()
        await self.ahk.set_send_level(1)
        await self.win.activate()
        await self.ahk.send('btw ')
        time.sleep(2)

        assert 'by the way' in await self.win.get_text()

    async def test_remove_hotstring(self):
        self.ahk.add_hotstring('btw', 'by the way')
        self.ahk.start_hotkeys()
        await self.ahk.set_send_level(1)
        await self.win.activate()
        self.ahk.remove_hotstring('btw')
        await self.ahk.send('btw ')
        time.sleep(2)
        assert 'by the way' not in await self.win.get_text()

    async def test_clear_hotstrings(self):
        self.ahk.add_hotstring('btw', 'by the way')
        self.ahk.start_hotkeys()
        await self.ahk.set_send_level(1)
        await self.win.activate()
        self.ahk.clear_hotstrings()
        await self.ahk.send('btw ')
        time.sleep(2)
        assert 'by the way' not in await self.win.get_text()

    async def test_hotstring_callback(self):
        with unittest.mock.MagicMock(return_value=None) as m:
            self.ahk.add_hotstring('btw', m)
            self.ahk.start_hotkeys()
            await self.ahk.set_send_level(1)
            await self.win.activate()
            await self.ahk.send('btw ')
            await async_sleep(1)
            m.assert_called()


class TestKeysAsyncV2(TestKeysAsync):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(version='v2')
        self.p = subprocess.Popen('notepad')
        time.sleep(1)
        self.win = await self.ahk.win_get(title='Untitled - Notepad')
        self.assertIsNotNone(self.win)
        await self.ahk.set_capslock_state('Off')
