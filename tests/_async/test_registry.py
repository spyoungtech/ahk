import pathlib
import subprocess
import tempfile
import time
import unittest.mock

import pytest

from ahk import AsyncAHK
from ahk import AsyncWindow
from ahk.message import AHKExecutionException


class TestScripts(unittest.IsolatedAsyncioTestCase):
    win: AsyncWindow

    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK()

    async def asyncTearDown(self) -> None:
        try:
            self.ahk._transport._proc.kill()
        except:
            pass
        try:
            await self.ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        except:
            pass
        time.sleep(0.2)

    async def test_reg_read_write_default_value_name(self):
        await self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', value='test')
        val = await self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        assert val == 'test'

    async def test_reg_write_explicit_value_name(self):
        await self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'foo', value='testfoo')
        val = await self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'foo')
        assert val == 'testfoo'

    async def test_reg_delete(self):
        await self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar', value='testbar')
        await self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar')
        await self.ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar')
        with pytest.raises(AHKExecutionException):
            await self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar')

    async def test_reg_delete_default(self):
        await self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', value='test')
        await self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        await self.ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        with pytest.raises(AHKExecutionException):
            await self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')


class TestScriptsV2(TestScripts):
    async def asyncSetUp(self) -> None:
        self.ahk = AsyncAHK(version='v2')
