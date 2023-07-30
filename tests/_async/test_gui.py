import asyncio
import time
import unittest

import pytest

from ahk import AsyncAHK

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep


class TestGui(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_msg_box(self):
        box = await self.ahk.msg_box(text='hello', title='test', timeout=3, blocking=False)
        await async_sleep(1)
        win = await self.ahk.win_get(title='test')
        assert win is not None
        with pytest.raises(TimeoutError):
            r = await box.result()
