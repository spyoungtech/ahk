import os
import sys
from unittest import mock

import pytest
from ahk import AHK
from ahk.script import DEFAULT_EXECUTABLE_PATH, ExecutableNotFoundError

project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)


def check_pwd():
    """
    Check the presence of autohotkey in present working directory.
    This can inadvertently affect test results, so we skip if it's present.
    This is due to the behavior of shutil.which on Windows
    REF: https://docs.python.org/3/library/shutil.html#shutil.which
    :return:
    """
    for name in os.listdir(os.getcwd()):
        if name.lower() == 'autohotkey.exe' or name.lower() == 'autohotkeya32':
            pytest.skip(
                'Skipping because autohotkey is in present directory (and will therefore always be found)')


def test_no_executable_raises_error():
    check_pwd()
    with mock.patch.dict(os.environ, {'PATH': ''}, clear=True):
        if not os.path.isfile(DEFAULT_EXECUTABLE_PATH):
            with pytest.raises(ExecutableNotFoundError):
                AHK()


def test_executable_path_from_env():
    check_pwd()
    with mock.patch.dict(os.environ, {'PATH': '', 'AHK_PATH': sys.executable}):
        # using sys.executable as a standin for any file with exe extension
        ahk = AHK()
        assert ahk.executable_path == sys.executable


def test_env_var_takes_precedence_over_path():
    check_pwd()
    actual_path = AHK().executable_path
    ahk_location = os.path.abspath(os.path.dirname(actual_path))
    with mock.patch.dict(os.environ, {'PATH': ahk_location, 'AHK_PATH': sys.executable}):
        # using sys.executable as a standin for any file with exe extension
        ahk = AHK()
        assert ahk.executable_path == sys.executable


def test_executable_from_path():
    check_pwd()
    actual_path = AHK().executable_path
    ahk_location = os.path.abspath(os.path.dirname(actual_path))
    with mock.patch.dict(os.environ, {'PATH': ahk_location}, clear=True):
        ahk = AHK()
        assert ahk.executable_path == actual_path


def test_executable_as_dir_raises_error():
    some_dir = os.path.abspath(os.path.dirname(__file__))
    with pytest.raises(ExecutableNotFoundError):
        AHK(executable_path=some_dir)


def test_file_without_exe_extension_warns():
    with pytest.warns(UserWarning):
        AHK(executable_path=os.path.abspath(__file__))
