import asyncio
import random
import string
import time
import unittest

import pytest

from ahk import AHK
from ahk.extensions import Extension


sleep = time.sleep

function_name = 'AHKDoSomething'

ext_text = f'''\
{function_name}(first, second) {{
    return FormatResponse("ahk.message.StringResponseMessage", Format("{{}} and {{}}", first, second))
}}
'''

async_extension = Extension(script_text=ext_text)


@async_extension.register
def do_something(ahk, first: str, second: str) -> str:
    res = ahk.function_call(function_name, [first, second])
    return res


class TestExtensions(unittest.TestCase):
    def setUp(self) -> None:
        self.ahk = AHK(extensions=[async_extension])

    def tearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_ext_explicit(self):
        res = self.ahk.do_something('foo', 'bar')
        assert res == 'foo and bar'


class TestExtensionsAuto(unittest.TestCase):
    def setUp(self) -> None:
        self.ahk = AHK(extensions='auto')

    def tearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_ext_auto(self):
        res = self.ahk.do_something('foo', 'bar')
        assert res == 'foo and bar'


class TestNoExtensions(unittest.TestCase):
    def setUp(self) -> None:
        self.ahk = AHK()
        self.ahk.get_mouse_position()  # cause daemon to start

    def tearDown(self) -> None:
        self.ahk._transport._proc.kill()
        time.sleep(0.2)

    def test_ext_no_ext(self):
        assert not hasattr(self.ahk, 'do_something')


class TestExtensionsV2(TestExtensions):
    def setUp(self) -> None:
        self.ahk = AHK(extensions=[async_extension], version='v2')


class TestExtensionsAutoV2(TestExtensionsAuto):
    def setUp(self) -> None:
        self.ahk = AHK(extensions='auto', version='v2')


class TestNoExtensionsV2(TestNoExtensions):
    def setUp(self) -> None:
        self.ahk = AHK(version='v2')
        self.ahk.get_mouse_position()  # cause daemon to start
