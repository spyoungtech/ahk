import asyncio
import time
import unittest

import pytest

from ahk import AsyncAHK
from ahk.extensions import Extension

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep

ext_text = '''\
AHKDoSomething(ByRef command) {
    global STRINGRESPONSEMESSAGE
    arg := command[2]
    return FormatResponse(STRINGRESPONSEMESSAGE, Format("test{}", arg))
}
'''

async_extension = Extension(script_text=ext_text)


@async_extension.register
async def do_something(ahk, arg: str) -> str:
    res = await ahk._transport.function_call('AHKDoSomething', [arg])
    return res


class TestExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions=[async_extension])

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext(self):
        res = await self.ahk.do_something('foo')
        assert res == 'testfoo'


class TestExtensionsAuto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions='auto')

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext(self):
        res = await self.ahk.do_something('foo')
        assert res == 'testfoo'


class TestNoExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()
        await self.ahk.get_mouse_position()  # cause daemon to start

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext(self):
        assert not hasattr(self.ahk, 'do_something')
