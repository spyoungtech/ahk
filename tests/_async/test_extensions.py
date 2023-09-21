import asyncio
import random
import string
import time
import unittest

import pytest

from ahk import AsyncAHK
from ahk.extensions import Extension

async_sleep = asyncio.sleep  # unasync: remove

sleep = time.sleep

function_name = 'AHKDoSomething'
function_name = 'AAHKDoSomething'  # unasync: remove

ext_text = f'''\
{function_name}(first, second) {{
    return FormatResponse("ahk.message.StringResponseMessage", Format("{{}} and {{}}", first, second))
}}
'''

async_extension = Extension(script_text=ext_text)


@async_extension.register
async def do_something(ahk, first: str, second: str) -> str:
    res = await ahk.function_call(function_name, [first, second])
    return res


class TestExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions=[async_extension])

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext_explicit(self):
        res = await self.ahk.do_something('foo', 'bar')
        assert res == 'foo and bar'


class TestExtensionsAuto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions='auto')

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext_auto(self):
        res = await self.ahk.do_something('foo', 'bar')
        assert res == 'foo and bar'


class TestNoExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()
        await self.ahk.get_mouse_position()  # cause daemon to start

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext_no_ext(self):
        assert not hasattr(self.ahk, 'do_something')


class TestExtensionsV2(TestExtensions):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions=[async_extension], version='v2')


class TestExtensionsAutoV2(TestExtensionsAuto):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions='auto', version='v2')


class TestNoExtensionsV2(TestNoExtensions):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(version='v2')
        await self.ahk.get_mouse_position()  # cause daemon to start
