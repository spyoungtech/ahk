import pathlib
import subprocess
import tempfile
import time
import unittest.mock

import pytest

from ahk import AHK
from ahk import Window
from ahk.message import AHKExecutionException


class TestScripts(unittest.TestCase):
    win: Window

    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        try:
            self.ahk._transport._proc.kill()
        except:
            pass
        try:
            self.ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        except:
            pass
        time.sleep(0.2)

    def test_reg_read_write_default_value_name(self):
        self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', value='test')
        val = self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        assert val == 'test'

    def test_reg_write_explicit_value_name(self):
        self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'foo', value='testfoo')
        val = self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'foo')
        assert val == 'testfoo'

    def test_reg_delete(self):
        self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar', value='testbar')
        self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar')
        self.ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar')
        with pytest.raises(AHKExecutionException):
            self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', 'bar')

    def test_reg_delete_default(self):
        self.ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\python-ahk', value='test')
        self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        self.ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')
        with pytest.raises(AHKExecutionException):
            self.ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\python-ahk')


class TestScriptsV2(TestScripts):
    def setUp(self) -> None:
        self.ahk = AHK(version='v2')
