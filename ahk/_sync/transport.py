from __future__ import annotations

import asyncio.subprocess
import atexit
import os
import subprocess
import sys
import warnings
from abc import ABC
from abc import abstractmethod
from io import BytesIO
from shutil import which
from typing import Any
from typing import AnyStr
from typing import Generic
from typing import List
from typing import Literal
from typing import Optional
from typing import overload
from typing import Protocol
from typing import runtime_checkable
from typing import Tuple
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

if TYPE_CHECKING:
    from ahk import Control
    from ahk import Window

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias, TypeGuard
else:
    from typing import TypeAlias, TypeGuard

from ahk._hotkey import ThreadedHotkeyTransport, Hotkey, Hotstring
from ahk.message import RequestMessage
from ahk.message import ResponseMessage
from ahk.message import Position

from concurrent.futures import Future, ThreadPoolExecutor

DEFAULT_EXECUTABLE_PATH = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'

T_SyncFuture = TypeVar('T_SyncFuture')


class AHKProtocolError(Exception):
    ...




class FutureResult(Generic[T_SyncFuture]):
    def __init__(self, future: Future[T_SyncFuture]):
        self._fut: Future[T_SyncFuture] = future

    def result(self, timeout: Optional[float] = None) -> T_SyncFuture:
        return self._fut.result(timeout=timeout)



SyncIOProcess: TypeAlias = 'subprocess.Popen[bytes]'


FunctionName = Literal[
    'AHKControlClick',
    'AHKControlGetPos',
    'AHKControlGetText',
    'AHKControlSend',
    'AHKGetCoordMode',
    'AHKGetSendLevel',
    'AHKGetTitleMatchMode',
    'AHKGetTitleMatchSpeed',
    'AHKImageSearch',
    'AHKKeyState',
    'AHKKeyWait',
    'AHKMouseClickDrag',
    'AHKMouseGetPos',
    'AHKMouseMove',
    'AHKPixelGetColor',
    'AHKPixelSearch',
    'AHKSend',
    'AHKSendEvent',
    'AHKSendInput',
    'AHKSendPlay',
    'AHKSendRaw',
    'AHKSetDetectHiddenWindows',
    'AHKSetCoordMode',
    'AHKSetSendLevel',
    'AHKSetTitleMatchMode',
    'AHKWinActivate',
    'AHKWinClose',
    'AHKWinExist',
    'AHKWinFromMouse',
    'AHKWinGetControlList',
    'AHKWinGetControlListHwnd',
    'AHKWinGetCount',
    'AHKWinGetExStyle',
    'AHKWinGetID',
    'AHKWinGetIDLast',
    'AHKWinGetList',
    'AHKWinGetMinMax',
    'AHKWinGetPID',
    'AHKWinGetPos',
    'AHKWinGetProcessName',
    'AHKWinGetProcessPath',
    'AHKWinGetStyle',
    'AHKWinGetText',
    'AHKWinGetTitle',
    'AHKWinGetTransColor',
    'AHKWinGetTransparent',
    'AHKWinHide',
    'AHKWinIsActive',
    'AHKWinIsAlwaysOnTop',
    'AHKWinMove',
    'AHKWinSetAlwaysOnTop',
    'AHKWinSetBottom',
    'AHKWinSetDisable',
    'AHKWinSetEnable',
    'AHKWinSetExStyle',
    'AHKWinSetRedraw',
    'AHKWinSetRegion',
    'AHKWinSetStyle',
    'AHKWinSetTitle',
    'AHKWinSetTop',
    'AHKWinSetTransColor',
    'AHKWinSetTransparent',
    'AHKWinShow',
    'AHKWindowList',
    'AHKWinWait',
    'AHKWinWaitActive',
    'AHKWinWaitNotActive',
    'AHKClick',
    'CoordMode',
    'AHKSetCapsLockState',
    'SetKeyDelay',
    'WinActivateBottom',
    'WinClick',
    'WinGet',
    'AHKWinGetClass',
    'WinHide',
    'AHKWinKill',
    'AHKWinMaximize',
    'AHKWinMinimize',
    'AHKWinRestore',
    'WinShow',
]


@runtime_checkable
class Killable(Protocol):
    def kill(self) -> None:
        ...


def kill(proc: Killable) -> None:
    try:
        proc.kill()
    except:  # noqa
        pass


def async_assert_send_nonblocking_type_correct(
    obj: Any,
) -> TypeGuard[
    Future[Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]]
]:
    return True


class SyncAHKProcess:
    def __init__(self, runargs: List[str]):
        self.runargs = runargs
        self._proc: Optional[SyncIOProcess] = None

    def start(self) -> None:
        self._proc = sync_create_process(self.runargs)
        atexit.register(kill, self._proc)
        return None


    def drain_stdin(self) -> None:
        assert isinstance(self._proc, subprocess.Popen)
        assert self._proc.stdin is not None
        self._proc.stdin.flush()
        return None

    def write(self, content: bytes) -> None:
        assert self._proc is not None
        assert self._proc.stdin is not None
        self._proc.stdin.write(content)

    def readline(self) -> bytes:
        assert self._proc is not None
        assert self._proc.stdout is not None
        line = self._proc.stdout.readline()
        assert isinstance(line, bytes)
        return line

    def kill(self) -> None:
        assert self._proc is not None, 'no process to kill'
        self._proc.kill()




def sync_create_process(runargs: List[str]) -> subprocess.Popen[bytes]:
    return subprocess.Popen(runargs, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)


class AhkExecutableNotFoundError(EnvironmentError):
    pass


def _resolve_executable_path(executable_path: Union[str, os.PathLike[AnyStr]] = '') -> str:
    if not executable_path:
        executable_path = (
            os.environ.get('AHK_PATH', '')
            or which('AutoHotkey.exe')
            or which('AutoHotkeyU64.exe')
            or which('AutoHotkeyU32.exe')
            or which('AutoHotkeyA32.exe')
            or ''
        )

    if not executable_path:
        if os.path.exists(DEFAULT_EXECUTABLE_PATH):
            executable_path = DEFAULT_EXECUTABLE_PATH

    if not executable_path:
        raise AhkExecutableNotFoundError(
            'Could not find AutoHotkey.exe on PATH. '
            'Provide the absolute path with the `executable_path` keyword argument '
            'or in the AHK_PATH environment variable. '
            'You may be able to resolve this error by installing the binary extra: pip install "ahk[binary]"'
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


class Transport(ABC):
    _started: bool = False

    def __init__(self, /, executable_path: Union[str, os.PathLike[AnyStr]] = '', **kwargs: Any):
        self._executable_path: str = _resolve_executable_path(executable_path=executable_path)
        self._hotkey_transport = ThreadedHotkeyTransport(executable_path=self._executable_path)
        pass

    def add_hotkey(self, hotkey: Hotkey) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._hotkey_transport.add_hotkey(hotkey=hotkey)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    def add_hotstring(self, hotstring: Hotstring) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._hotkey_transport.add_hotstring(hotstring=hotstring)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    def start_hotkeys(self) -> None:
        return self._hotkey_transport.start()

    def stop_hotkeys(self) -> None:
        return self._hotkey_transport.stop()

    def init(self) -> None:
        self._started = True
        return None

    # fmt: off
    @overload
    def function_call(self, function_name: Literal['AHKWinExist'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, FutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKImageSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Tuple[int, int], None, FutureResult[Union[Tuple[int, int], None]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKPixelGetColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, FutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKPixelSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Optional[Tuple[int, int]], FutureResult[Optional[Tuple[int, int]]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKMouseGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Tuple[int, int], FutureResult[Tuple[int, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKKeyState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[int, float, str, None, FutureResult[None], FutureResult[str], FutureResult[int], FutureResult[float]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKMouseMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['CoordMode'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKClick'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKMouseClickDrag'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKKeyWait'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[int, FutureResult[int]]: ...
    @overload
    def function_call(self, function_name: Literal['SetKeyDelay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSendRaw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSendInput'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSendEvent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSendPlay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSetCapsLockState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, FutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetClass'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, FutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetText'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, FutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinActivate'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinActivateBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinClose'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinHide'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinKill'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinMaximize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinMinimize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinRestore'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinShow'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWindowList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[List[Window], FutureResult[List[Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKControlSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinFromMouse'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Optional[Window], FutureResult[Optional[Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinIsAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Optional[bool], FutureResult[Optional[bool]]]: ...
    @overload
    def function_call(self, function_name: Literal['WinClick'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[Position, None], FutureResult[Union[None, Position]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, Window], FutureResult[Union[None, Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetIDLast'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, Window], FutureResult[Union[None, Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetPID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[int, None], FutureResult[Union[int, None]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetProcessName'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], FutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetProcessPath'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], FutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetCount'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[int, FutureResult[int]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[List[Window], FutureResult[List[Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetMinMax'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, int], FutureResult[Union[None, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetControlList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[List[Control], None, FutureResult[Union[List[Control], None]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, int], FutureResult[Union[None, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], FutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], FutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], FutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetDisable'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetEnable'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetRedraw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, FutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, FutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetRegion'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, FutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSetDetectHiddenWindows'], args: Optional[List[str]] = None) -> None: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinSetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKSetTitleMatchMode'], args: Optional[List[str]] = None) -> None: ...
    @overload
    def function_call(self, function_name: Literal['AHKGetTitleMatchMode']) -> str: ...
    @overload
    def function_call(self, function_name: Literal['AHKGetTitleMatchSpeed']) -> str: ...
    @overload
    def function_call(self, function_name: Literal['AHKControlGetText'], args: Optional[List[str]] = None, *, engine: Optional[AHK] = None, blocking: bool = True) -> Union[str, FutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKControlClick'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKControlGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[Position, FutureResult[Position]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKGetCoordMode'], args: List[str]) -> str: ...
    @overload
    def function_call(self, function_name: Literal['AHKSetCoordMode'], args: List[str]) -> None: ...
    @overload
    def function_call(self, function_name: Literal['AHKGetSendLevel']) -> int: ...
    @overload
    def function_call(self, function_name: Literal['AHKSetSendLevel'], args: List[str]) -> None: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinWait'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Window, FutureResult[Window]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinWaitActive'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Window, FutureResult[Window]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinWaitNotActive'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Window, FutureResult[Window]]: ...

    @overload
    def function_call(self, function_name: Literal['AHKWinShow'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinHide'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, FutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinIsActive'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, FutureResult[bool]]: ...

    # @overload
    # async def function_call(self, function_name: Literal['HideTrayTip'], args: Optional[List[str]] = None) -> None: ...
    # @overload
    # async def function_call(self, function_name: Literal['BaseCheck'], args: Optional[List[str]] = None) -> None: ...
    # @overload
    # async def function_call(self, function_name: Literal['WinWait'], args: Optional[List[str]] = None) -> str: ...
    # @overload
    # async def function_call(self, function_name: Literal['WinWaitActive'], args: Optional[List[str]] = None) -> str: ...
    # @overload
    # async def function_call(self, function_name: Literal['WinWaitNotActive'], args: Optional[List[str]] = None) -> str: ...
    # @overload
    # async def function_call(self, function_name: Literal['WinWaitClose'], args: Optional[List[str]] = None) -> None: ...
    # @overload
    # async def function_call(self, function_name: Literal['RegRead'], args: Optional[List[str]] = None) -> None: ...
    # @overload
    # async def function_call(self, function_name: Literal['SetRegView'], args: Optional[List[str]] = None) -> None: ...
    # @overload
    # async def function_call(self, function_name: Literal['RegWrite'], args: Optional[List[str]] = None) -> None: ...
    # @overload
    # async def function_call(self, function_name: Literal['RegDelete'], args: Optional[List[str]] = None) -> None: ...

    # fmt: on

    def function_call(
        self,
        function_name: FunctionName,
        args: Optional[List[str]] = None,
        blocking: bool = True,
        engine: Optional[AHK] = None,
    ) -> Any:
        if not self._started:
            self.init()
        request = RequestMessage(function_name=function_name, args=args)
        if blocking:
            return self.send(request, engine=engine)
        else:
            return self.send_nonblocking(request, engine=engine)

    @abstractmethod
    def send(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]:
        return NotImplemented


    @abstractmethod
    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> FutureResult[Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]]:
        return NotImplemented


class DaemonProcessTransport(Transport):
    def __init__(self, *, executable_path: Union[str, os.PathLike[AnyStr]] = ''):
        self._proc: Optional[SyncAHKProcess]
        self._proc = None
        super().__init__(executable_path=executable_path)

    def init(self) -> None:
        self.start()
        super().init()
        return None

    def start(self) -> None:
        assert self._proc is None, 'cannot start a process twice'
        daemon_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../daemon.ahk'))
        runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', daemon_script]
        self._proc = SyncAHKProcess(runargs=runargs)
        self._proc.start()

    def _create_process(self) -> SyncAHKProcess:
        daemon_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../daemon.ahk'))
        runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', daemon_script]
        proc = SyncAHKProcess(runargs=runargs)
        proc.start()
        return proc

    def _send_nonblocking(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]:
        msg = request.format()
        proc = self._create_process()
        try:
            proc.write(msg)
            proc.drain_stdin()
            tom = proc.readline()
            num_lines = proc.readline()
            content_buffer = BytesIO()
            content_buffer.write(tom)
            content_buffer.write(num_lines)
            for _ in range(int(num_lines) + 1):
                part = proc.readline()
                content_buffer.write(part)
            content = content_buffer.getvalue()[:-1]
        except Exception:
            raise
        finally:
            try:
                proc.kill()
            except:  # noqa
                pass
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore


    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> FutureResult[Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]]:
        # this is only used by the sync implementation
        pool = ThreadPoolExecutor(max_workers=1)
        fut = pool.submit(self._send_nonblocking, request=request, engine=engine)
        pool.shutdown(wait=False)
        assert async_assert_send_nonblocking_type_correct(
            fut
        )  # workaround to get mypy correctness in sync and async implementation
        return FutureResult(fut)

    def send(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[Control]]:
        msg = request.format()
        assert self._proc is not None
        self._proc.write(msg)
        self._proc.drain_stdin()
        tom = self._proc.readline()
        num_lines = self._proc.readline()
        content_buffer = BytesIO()
        content_buffer.write(tom)
        content_buffer.write(num_lines)
        try:
            lines_to_read = int(num_lines) + 1
        except ValueError:
            raise AHKProtocolError(
                'Unexpected data received. This is usually the result of an unhandled error in the AHK process.'
            )
        for _ in range(lines_to_read):
            part = self._proc.readline()
            content_buffer.write(part)
        content = content_buffer.getvalue()[:-1]
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore


if TYPE_CHECKING:
    from .engine import AHK
