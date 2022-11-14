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
from typing import Callable
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
    from ahk import AsyncControl
    from ahk import AsyncWindow

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias, TypeGuard
else:
    from typing import TypeAlias, TypeGuard

from ahk.hotkey import ThreadedHotkeyTransport, Hotkey, Hotstring
from concurrent.futures import Future, ThreadPoolExecutor

DEFAULT_EXECUTABLE_PATH = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'

T_AsyncFuture = TypeVar('T_AsyncFuture')  # unasync: remove
T_SyncFuture = TypeVar('T_SyncFuture')


class AsyncFutureResult(Generic[T_AsyncFuture]):  # unasync: remove
    def __init__(self, task: asyncio.Task[T_AsyncFuture]):
        self._task: asyncio.Task[T_AsyncFuture] = task

    async def result(self) -> T_AsyncFuture:
        return await self._task


class FutureResult(Generic[T_SyncFuture]):
    def __init__(self, future: Future[T_SyncFuture]):
        self._fut: Future[T_SyncFuture] = future

    def result(self, timeout: Optional[float] = None) -> T_SyncFuture:
        return self._fut.result(timeout=timeout)


AsyncIOProcess: TypeAlias = asyncio.subprocess.Process  # unasync: remove

SyncIOProcess: TypeAlias = 'subprocess.Popen[bytes]'


FunctionName = Literal[
    'AHKControlClick',
    'AHKControlGetPos',
    'AHKControlGetText',
    'AHKControlSend',
    'AHKGetTitleMatchMode',
    'AHKGetTitleMatchSpeed',
    'AHKImageSearch',
    'AHKKeyState',
    'AHKKeyWait',
    'AHKMouseGetPos',
    'AHKMouseMove',
    'AHKSend',
    'AHKSendEvent',
    'AHKSendInput',
    'AHKSendPlay',
    'AHKSendRaw',
    'AHKSetDetectHiddenWindows',
    'AHKSetTitleMatchMode',
    'AHKWinClose',
    'AHKWinExist',
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
    'AHKWindowList',
    'Click',
    'CoordMode',
    'FromMouse',
    'MouseClickDrag',
    'PixelGetColor',
    'PixelSearch',
    'SetCapsLockState',
    'SetKeyDelay',
    'WinActivate',
    'WinActivateBottom',
    'WinClick',
    'WinGet',
    'WinGetClass',
    'WinHide',
    'WinKill',
    'WinMaximize',
    'WinMinimize',
    'WinRestore',
    'WinSend',
    'WinSendRaw',
    'WinSet',
    'WinSetTitle',
    'WinShow',
]


@runtime_checkable
class Killable(Protocol):
    def kill(self) -> None:
        ...


def kill(proc: Killable) -> None:
    try:
        proc.kill()
    except:
        pass


def async_assert_send_nonblocking_type_correct(
    obj: Any,
) -> TypeGuard[
    Future[Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]]
]:
    return True


class AsyncAHKProcess:
    def __init__(self, runargs: List[str]):
        self.runargs = runargs
        self._proc: Optional[AsyncIOProcess] = None

    async def start(self) -> None:
        self._proc = await async_create_process(self.runargs)
        atexit.register(kill, self._proc)
        return None

    async def adrain_stdin(self) -> None:  # unasync: remove
        assert self._proc is not None
        assert self._proc.stdin is not None
        await self._proc.stdin.drain()
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

    async def readline(self) -> bytes:
        assert self._proc is not None
        assert self._proc.stdout is not None
        line = await self._proc.stdout.readline()
        assert isinstance(line, bytes)
        return line

    def kill(self) -> None:
        assert self._proc is not None
        self._proc.kill()


async def async_create_process(runargs: List[str]) -> asyncio.subprocess.Process:  # unasync: remove
    return await asyncio.subprocess.create_subprocess_exec(
        *runargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


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


class AsyncTransport(ABC):
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

    async def init(self) -> None:
        self._started = True
        return None

    # fmt: off
    @overload
    async def function_call(self, function_name: Literal['AHKWinExist'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKImageSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Tuple[int, int], None, AsyncFutureResult[Union[Tuple[int, int], None]]]: ...
    @overload
    async def function_call(self, function_name: Literal['PixelGetColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['PixelSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Tuple[int, int], AsyncFutureResult[Tuple[int, int]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMouseGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Tuple[int, int], AsyncFutureResult[Tuple[int, int]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKKeyState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMouseMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['CoordMode'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['Click'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['MouseClickDrag'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKKeyWait'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[int, AsyncFutureResult[int]]: ...
    @overload
    async def function_call(self, function_name: Literal['SetKeyDelay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendRaw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendInput'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendEvent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendPlay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['SetCapsLockState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinGetClass'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetText'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinActivate'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinActivateBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinClose'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinHide'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinKill'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinMaximize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinMinimize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinRestore'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinShow'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWindowList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinSendRaw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKControlSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['FromMouse'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinGet'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinSet'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinSetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinIsAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Optional[bool], AsyncFutureResult[Optional[bool]]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinClick'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # @overload
    # async def function_call(self, function_name: Literal['AHKWinGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK) = None -> Union[TupleResponseMessage, AsyncFutureResult[TupleResponseMessage]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, AsyncWindow], AsyncFutureResult[Union[None, AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetIDLast'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, AsyncWindow], AsyncFutureResult[Union[None, AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetPID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[int, None], AsyncFutureResult[Union[int, None]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetProcessName'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetProcessPath'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetCount'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[int, AsyncFutureResult[int]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetMinMax'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, int], AsyncFutureResult[Union[None, int]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetControlList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[List[AsyncControl], None, AsyncFutureResult[Union[List[AsyncControl], None]]]: ...
    # @overload
    # async def function_call(self, function_name: Literal['AHKWinGetControlListHwnd'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[List[AsyncControl], AsyncFutureResult[List[AsyncControl]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, int], AsyncFutureResult[Union[None, int]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...

    @overload
    async def function_call(self, function_name: Literal['AHKWinSetAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetDisable'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetEnable'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetRedraw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetRegion'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[bool, AsyncFutureResult[bool]]: ...

    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[None, AsyncFutureResult[None]]: ...

    @overload
    async def function_call(self, function_name: Literal['AHKSetDetectHiddenWindows'], args: Optional[List[str]] = None) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetTitleMatchMode'], args: Optional[List[str]] = None) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetTitleMatchMode']) -> str: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetTitleMatchSpeed']) -> str: ...

    @overload
    async def function_call(self, function_name: Literal['AHKControlGetText'], args: Optional[List[str]] = None, *, engine: Optional[AsyncAHK] = None, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...

    @overload
    async def function_call(self, function_name: Literal['AHKControlClick'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    @overload
    async def function_call(self, function_name: Literal['AHKControlGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[Tuple[int, int, int, int], AsyncFutureResult[Tuple[int, int, int, int]]]: ...
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

    async def function_call(
        self,
        function_name: FunctionName,
        args: Optional[List[str]] = None,
        blocking: bool = True,
        engine: Optional[AsyncAHK] = None,
    ) -> Any:
        if not self._started:
            await self.init()
        request = RequestMessage(function_name=function_name, args=args)
        if blocking:
            return await self.send(request, engine=engine)
        else:
            return await self.a_send_nonblocking(request, engine=engine)

    @abstractmethod
    async def send(
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]:
        return NotImplemented

    @abstractmethod  # unasync: remove
    async def a_send_nonblocking(  # unasync: remove
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> AsyncFutureResult[
        Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]
    ]:
        return NotImplemented

    @abstractmethod
    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> FutureResult[Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]]:
        return NotImplemented


class AsyncDaemonProcessTransport(AsyncTransport):
    def __init__(self, *, executable_path: Union[str, os.PathLike[AnyStr]] = ''):
        self._proc: Optional[AsyncAHKProcess]
        self._proc = None
        super().__init__(executable_path=executable_path)

    async def init(self) -> None:
        await self.start()
        await super().init()
        return None

    async def start(self) -> None:
        assert self._proc is None, 'cannot start a process twice'
        daemon_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../daemon.ahk'))
        runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', daemon_script]
        self._proc = AsyncAHKProcess(runargs=runargs)
        await self._proc.start()

    async def _create_process(self) -> AsyncAHKProcess:
        daemon_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../daemon.ahk'))
        runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', daemon_script]
        proc = AsyncAHKProcess(runargs=runargs)
        await proc.start()
        return proc

    async def _send_nonblocking(
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]:
        msg = request.format()
        proc = await self._create_process()
        try:
            proc.write(msg)
            await proc.adrain_stdin()
            tom = await proc.readline()
            num_lines = await proc.readline()
            content_buffer = BytesIO()
            content_buffer.write(tom)
            content_buffer.write(num_lines)
            for _ in range(int(num_lines) + 1):
                part = await proc.readline()
                content_buffer.write(part)
            content = content_buffer.getvalue()[:-1]
        except Exception:
            raise
        finally:
            try:
                proc.kill()
            except:
                pass
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore

    async def a_send_nonblocking(  # unasync: remove
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> AsyncFutureResult[
        Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]
    ]:
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._send_nonblocking(request=request, engine=engine))
        return AsyncFutureResult(task)

    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> FutureResult[Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]]:
        # this is only used by the sync implementation
        pool = ThreadPoolExecutor(max_workers=1)
        fut = pool.submit(self._send_nonblocking, request=request, engine=engine)
        pool.shutdown(wait=False)
        assert async_assert_send_nonblocking_type_correct(
            fut
        )  # workaround to get mypy correctness in sync and async implementation
        return FutureResult(fut)

    async def send(
        self, request: RequestMessage, engine: Optional[AsyncAHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]:
        msg = request.format()
        assert self._proc is not None
        self._proc.write(msg)
        await self._proc.adrain_stdin()
        tom = await self._proc.readline()
        num_lines = await self._proc.readline()
        content_buffer = BytesIO()
        content_buffer.write(tom)
        content_buffer.write(num_lines)
        for _ in range(int(num_lines) + 1):
            part = await self._proc.readline()
            content_buffer.write(part)
        content = content_buffer.getvalue()[:-1]
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore


from ahk.message import RequestMessage
from ahk.message import ResponseMessage


if TYPE_CHECKING:
    from .engine import AsyncAHK
