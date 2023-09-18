import asyncio
import time
import unittest.mock

from ahk import AsyncAHK

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep


class TestWindowAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_clipboard(self):
        await self.ahk.set_clipboard('foo')
        contents = await self.ahk.get_clipboard()
        assert contents == 'foo'

    async def test_clipboard_all(self):
        await self.ahk.set_clipboard('Hello \N{EARTH GLOBE AMERICAS}')
        data = await self.ahk.get_clipboard_all()
        await self.ahk.set_clipboard('foo')
        assert data != await self.ahk.get_clipboard_all()
        await self.ahk.set_clipboard_all(data)
        assert data == await self.ahk.get_clipboard_all()
        assert await self.ahk.get_clipboard() == 'Hello \N{EARTH GLOBE AMERICAS}'

    async def test_on_clipboard_change(self):
        with unittest.mock.MagicMock(return_value=None) as m:
            self.ahk.on_clipboard_change(m)
            self.ahk.start_hotkeys()
            await self.ahk.set_clipboard('foo')
            await self.ahk.set_clipboard('bar')
            await async_sleep(1)
            m.assert_called()


class TestWindowAsyncV2(TestWindowAsync):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(version='v2')
