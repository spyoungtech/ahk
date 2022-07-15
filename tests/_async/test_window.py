import asyncio
import os
import subprocess
import sys
import time
from unittest import IsolatedAsyncioTestCase

from ahk import AsyncAHK
from ahk import AsyncWindow


# class TestWindowAsync(IsolatedAsyncioTestCase):
#     win: AsyncWindow
#
#     async def asyncSetUp(self) -> None:
#         self.ahk = AsyncAHK()
#         self.p = subprocess.Popen('notepad')
#         time.sleep(1)
#         self.win = await self.ahk.win_get(title='Untitled - Notepad')
#         self.assertIsNotNone(self.win)
#
#     async def test_close(self):
#         await self.win.close()
#         await asyncio.sleep(0.2)
#         self.assertFalse(await self.win.exists())
#         self.assertFalse(await self.win.exist)
