import asyncio
import os
import subprocess
import sys
import time
from unittest import IsolatedAsyncioTestCase

from ahk import AsyncAHK
from ahk import AsyncWindow


class TestWindowAsync(IsolatedAsyncioTestCase):
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
        self.ahk._transport._proc.kill()

    async def test_set_capslock(self):
        await self.ahk.set_capslock_state('On')
        assert await self.ahk.key_state('CapsLock', mode='T') == 1
