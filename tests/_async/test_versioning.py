import shutil
import subprocess
import time
from unittest import IsolatedAsyncioTestCase

import pytest

from ahk import AsyncAHK

V2_EXECUTABLE = shutil.which('AutoHotkeyV2.exe')
V1_EXECUTABLE = shutil.which('AutoHotkey.exe')


class TestVersion(IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        subprocess.run(['TASKKILL', '/F', '/IM', 'AutoHotkey*.exe'], capture_output=True)
        time.sleep(0.2)

    async def test_default_is_v1(self):
        ahk = AsyncAHK()
        assert await ahk.get_major_version() == 'v1'

    async def test_v1_explicit(self):
        ahk = AsyncAHK(version='v1')
        assert await ahk.get_major_version() == 'v1'

    async def test_v2_explicit(self):
        ahk = AsyncAHK(version='v2')
        assert await ahk.get_major_version() == 'v2'

    async def test_autodetect_v2(self):
        ahk = AsyncAHK(executable_path=V2_EXECUTABLE)
        assert await ahk.get_major_version() == 'v2'

    async def test_autodetect_v1(self):
        ahk = AsyncAHK(executable_path=V1_EXECUTABLE)
        assert await ahk.get_major_version() == 'v1'

    async def test_mismatch_autodetect_raises_error_v1_v2(self):
        with pytest.raises(RuntimeError):
            ahk = AsyncAHK(executable_path=V1_EXECUTABLE, version='v2')

    async def test_mismatch_autodetect_raises_error_v2_v1(self):
        with pytest.raises(RuntimeError):
            ahk = AsyncAHK(executable_path=V2_EXECUTABLE, version='v1')
