import enum
import logging
import os
import re
import subprocess
import warnings
from shutil import which
from typing import Literal
from typing import Optional

from ahk.exceptions import AhkExecutableNotFoundError

HOTKEY_ESCAPE_SEQUENCE_MAP = {
    '\n': '`n',
    '\t': '`t',
    '\r': '`r',
    '\a': '`a',
    '\b': '`b',
    '\f': '`f',
    '\v': '`v',
    ',': '`,',
    '%': '`%',
    '`': '``',
    ';': '`;',
    ':': '`:',
}

ESCAPE_SEQUENCE_MAP = {
    '!': '{!}',
    '^': '{^}',
    '+': '{+}',
    '{': '{{}',
    '}': '{}}',
    '#': '{#}',
    '=': '{=}',
}

_TRANSLATION_TABLE = str.maketrans(ESCAPE_SEQUENCE_MAP)

_HOTKEY_TRANSLATION_TABLE = str.maketrans(HOTKEY_ESCAPE_SEQUENCE_MAP)


def hotkey_escape(s: str) -> str:
    return s.translate(_HOTKEY_TRANSLATION_TABLE)


def type_escape(s: str) -> str:
    return s.translate(_TRANSLATION_TABLE)


class MsgBoxButtons(enum.IntEnum):
    OK = 0
    OK_CANCEL = 1
    ABORT_RETRY_IGNORE = 2
    YES_NO_CANCEL = 3
    YES_NO = 4
    RETRY_CANCEL = 5
    CANCEL_TRYAGAIN_CONTINUE = 6


class MsgBoxIcon(enum.IntEnum):
    HAND = 16
    QUESTION = 32
    EXCLAMATION = 48
    ASTERISK = 64


class MsgBoxDefaultButton(enum.IntEnum):
    SECOND = 256
    THIRD = 512
    FOURTH = 768


class MsgBoxModality(enum.IntEnum):
    SYSTEM_MODAL = 4096
    TASK_MODAL = 8192
    ALWAYS_ON_TOP = 262144


class MsgBoxOtherOptions(enum.IntEnum):
    HELP_BUTTON = 16384
    TEXT_RIGHT_JUSTIFIED = 524288
    RIGHT_TO_LEFT_READING_ORDER = 1048576


DEFAULT_EXECUTABLE_PATH = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'
DEFAULT_EXECUTABLE_PATH_V2 = r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'


def _resolve_executable_path(executable_path: str = '', version: Optional[Literal['v1', 'v2']] = None) -> str:
    if not executable_path:
        executable_path = (
            os.environ.get('AHK_PATH', '')
            or (which('AutoHotkeyV2.exe') if version == 'v2' else '')
            or (which('AutoHotkey32.exe') if version == 'v2' else '')
            or (which('AutoHotkey64.exe') if version == 'v2' else '')
            or which('AutoHotkey.exe')
            or (which('AutoHotkeyU64.exe') if version != 'v2' else '')
            or (which('AutoHotkeyU32.exe') if version != 'v2' else '')
            or (which('AutoHotkeyA32.exe') if version != 'v2' else '')
            or ''
        )

    if not executable_path:
        if version == 'v2':
            if os.path.exists(DEFAULT_EXECUTABLE_PATH_V2):
                executable_path = DEFAULT_EXECUTABLE_PATH_V2
        else:
            if os.path.exists(DEFAULT_EXECUTABLE_PATH):
                executable_path = DEFAULT_EXECUTABLE_PATH

    if not executable_path:
        raise AhkExecutableNotFoundError(
            'Could not find AutoHotkey.exe on PATH. '
            'Provide the absolute path with the `executable_path` keyword argument '
            'or in the AHK_PATH environment variable. '
            'You can likely resolve this error simply by installing the binary extra with the following command:\n\tpip install "ahk[binary]"'
        )

    if not os.path.exists(executable_path):
        raise AhkExecutableNotFoundError(f"executable_path does not seems to exist: '{executable_path}' not found")

    if os.path.isdir(executable_path):
        raise AhkExecutableNotFoundError(
            f'The path {executable_path} appears to be a directory, but should be a file.'
            ' Please specify the *full path* to the autohotkey.exe executable file'
        )
    executable_path = str(executable_path)
    if not executable_path.endswith('.exe'):
        warnings.warn(
            'executable_path does not appear to have a .exe extension. This may be the result of a misconfiguration.'
        )

    return executable_path


_version_detection_script = '''\
#NoTrayIcon
version := Format("{}", A_AhkVersion)
filename := "*"
encoding := "UTF-8"
mode := "w"
stdout := FileOpen(filename, mode, encoding)
stdout.Write(version)
stdout.Read(0)
'''


def _get_executable_version(executable_path: str) -> str:
    process = subprocess.Popen(
        [executable_path, '/ErrorStdout', '/CP65001', '*'],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(_version_detection_script, timeout=2)
    assert re.match(r'^\d+\.', stdout)
    return stdout.strip()


def _get_executable_major_version(executable_path: str) -> Literal['v1', 'v2']:
    version = _get_executable_version(executable_path)
    match = re.match(r'^(\d+)\.', version)
    if not match:
        raise ValueError(f'Unexpected version {version!r}')
    major_version = match.group(1)
    if major_version == '1':
        return 'v1'
    elif major_version == '2':
        return 'v2'
    else:
        raise ValueError(f'Unexpected version {version!r}')


def try_remove(name: str) -> None:
    try:
        os.remove(name)
    except Exception as e:
        logging.debug(f'Ignoring removal exception {e}')
