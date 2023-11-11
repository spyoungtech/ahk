import shutil
import subprocess
import time
from unittest import TestCase

import pytest

from ahk import AHK

V2_EXECUTABLE = shutil.which('AutoHotkeyV2.exe')
V1_EXECUTABLE = shutil.which('AutoHotkey.exe')


class TestVersion(TestCase):
    def tearDown(self) -> None:
        subprocess.run(['TASKKILL', '/F', '/IM', 'AutoHotkey*.exe'], capture_output=True)
        time.sleep(0.2)

    def test_default_is_v1(self):
        ahk = AHK()
        assert ahk.get_major_version() == 'v1'

    def test_v1_explicit(self):
        ahk = AHK(version='v1')
        assert ahk.get_major_version() == 'v1'

    def test_v2_explicit(self):
        ahk = AHK(version='v2')
        assert ahk.get_major_version() == 'v2'

    def test_autodetect_v2(self):
        ahk = AHK(executable_path=V2_EXECUTABLE)
        assert ahk.get_major_version() == 'v2'

    def test_autodetect_v1(self):
        ahk = AHK(executable_path=V1_EXECUTABLE)
        assert ahk.get_major_version() == 'v1'

    def test_mismatch_autodetect_raises_error_v1_v2(self):
        with pytest.raises(RuntimeError):
            ahk = AHK(executable_path=V1_EXECUTABLE, version='v2')

    def test_mismatch_autodetect_raises_error_v2_v1(self):
        with pytest.raises(RuntimeError):
            ahk = AHK(executable_path=V2_EXECUTABLE, version='v1')
