import asyncio
import os
import pathlib
import subprocess
import sys
import time
from unittest import IsolatedAsyncioTestCase
from unittest import mock

from ahk import AsyncAHK
from ahk import AsyncWindow

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep


class TestScripts(IsolatedAsyncioTestCase):
    win: AsyncWindow

    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()

    async def asyncTearDown(self) -> None:
        try:
            self.ahk._transport._proc.kill()
        except:
            pass
        time.sleep(0.2)

    async def test_script_missing_makes_tempfile(self):
        with mock.patch('os.path.exists', new=mock.Mock(return_value=False)):
            pos = await self.ahk.get_mouse_position()
            path = pathlib.Path(self.ahk._transport._proc.runargs[-1])
            filename = path.name
            assert filename.startswith('python-ahk-')
            assert filename.endswith('.ahk')
            assert isinstance(pos, tuple) and isinstance(pos[0], int)
