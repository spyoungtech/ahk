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
{function_name}(ByRef command) {{
    arg := command[2]
    return FormatResponse("ahk.message.StringResponseMessage", Format("test{{}}", arg))
}}
'''

async_extension = Extension(script_text=ext_text)


@async_extension.register
async def do_something(ahk, arg: str) -> str:
    res = await ahk.function_call(function_name, [arg])
    return res


class TestExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions=[async_extension])

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext_explicit(self):
        res = await self.ahk.do_something('foo')
        assert res == 'testfoo'


class TestExtensionsAuto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(extensions='auto')

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext_auto(self):
        res = await self.ahk.do_something('foo')
        assert res == 'testfoo'


class TestNoExtensions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()
        await self.ahk.get_mouse_position()  # cause daemon to start

    async def asyncTearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    async def test_ext_no_ext(self):
        assert not hasattr(self.ahk, 'do_something')
