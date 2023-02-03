import time
from unittest import IsolatedAsyncioTestCase

from ahk import AsyncAHK


class TestWindowAsync(IsolatedAsyncioTestCase):
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
