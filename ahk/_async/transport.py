from __future__ import annotations

import asyncio.subprocess
import atexit
import os
import re
import subprocess
import sys
import tempfile
import threading
import warnings
from abc import ABC
from abc import abstractmethod
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Any
from typing import Callable
from typing import Generic
from typing import List
from typing import Literal
from typing import Optional
from typing import overload
from typing import Protocol
from typing import runtime_checkable
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

import jinja2

from ahk._constants import DAEMON_SCRIPT_TEMPLATE as _DAEMON_SCRIPT_TEMPLATE
from ahk._constants import DAEMON_SCRIPT_V2_TEMPLATE as _DAEMON_SCRIPT_V2_TEMPLATE
from ahk._hotkey import Hotkey
from ahk._hotkey import Hotstring
from ahk._hotkey import ThreadedHotkeyTransport
from ahk._types import Coordinates
from ahk._types import FunctionName
from ahk._types import Position
from ahk._utils import _version_detection_script
from ahk._utils import try_remove
from ahk.directives import Directive
from ahk.exceptions import AHKProtocolError
from ahk.extensions import _resolve_includes
from ahk.extensions import Extension
from ahk.message import _message_registry
from ahk.message import RequestMessage
from ahk.message import ResponseMessage


if TYPE_CHECKING:
    from ahk import AsyncControl
    from ahk import AsyncWindow

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias, TypeGuard
else:
    from typing import TypeAlias, TypeGuard

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

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


@runtime_checkable
class Killable(Protocol):
    def kill(self) -> None: ...


def kill(proc: Killable) -> None:
    try:
        proc.kill()
    except:  # noqa
        pass


def async_assert_send_nonblocking_type_correct(
    obj: Any,
) -> TypeGuard[
    Future[
        Union[None, Coordinates, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]
    ]
]:
    return True


class Communicable(Protocol):
    runargs: List[str]

    async def start(self, atexit_cleanup: bool = True) -> None: ...
    def astart(self, *args: Any, **kwargs: Any) -> None: ...  # unasync: remove

    def communicate(self, input_bytes: Optional[bytes], timeout: Optional[int] = None) -> Tuple[bytes, bytes]: ...

    async def acommunicate(  # unasync: remove
        self, input_bytes: Optional[bytes], timeout: Optional[int] = None
    ) -> Tuple[bytes, bytes]: ...

    @property
    def returncode(self) -> Optional[int]: ...

    def kill(self) -> None: ...


class AsyncAHKProcess:
    def __init__(self, runargs: List[str]):
        self.runargs = runargs
        self._proc: Optional[AsyncIOProcess] = None

    @property
    def returncode(self) -> Optional[int]:
        assert self._proc is not None
        return self._proc.returncode

    def astart(self, *args: Any, **kwargs: Any) -> None: ...  # unasync: remove

    async def start(self, atexit_cleanup: bool = True) -> None:
        self._proc = await async_create_process(self.runargs)
        if atexit_cleanup:
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

    async def read(self) -> bytes:
        assert self._proc is not None
        assert self._proc.stdout is not None
        b = await self._proc.stdout.read()
        assert isinstance(b, bytes)
        return b

    def kill(self) -> None:
        assert self._proc is not None, 'no process to kill'
        self._proc.kill()

    async def acommunicate(  # unasync: remove
        self, input_bytes: Optional[bytes] = None, timeout: Optional[int] = None
    ) -> Tuple[bytes, bytes]:
        assert self._proc is not None
        if timeout is not None:  # unasync: remove
            raise RuntimeError('timeout not supported in async api')
        return await self._proc.communicate(input=input_bytes)

    def communicate(self, input_bytes: Optional[bytes] = None, timeout: Optional[int] = None) -> Tuple[bytes, bytes]:
        assert self._proc is not None
        assert isinstance(self._proc, subprocess.Popen)
        return self._proc.communicate(input=input_bytes, timeout=timeout)

    async def __aenter__(self) -> Self:
        await self.start(atexit_cleanup=False)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> Literal[False]:
        try:
            self.kill()
        except Exception:
            pass
        return False


async def async_create_process(runargs: List[str]) -> asyncio.subprocess.Process:  # unasync: remove
    return await asyncio.subprocess.create_subprocess_exec(
        *runargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )


def sync_create_process(runargs: List[str]) -> subprocess.Popen[bytes]:
    return subprocess.Popen(runargs, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)


class AsyncTransport(ABC):
    _started: bool = False

    def __init__(
        self,
        /,
        directives: Optional[list[Union[Directive, Type[Directive]]]] = None,
        version: Optional[Literal['v1', 'v2']] = 'v1',
        hotkey_transport: Optional[ThreadedHotkeyTransport] = None,
        **kwargs: Any,
    ):
        self._hotkey_transport = hotkey_transport
        self._directives: list[Union[Directive, Type[Directive]]] = directives or []
        self._version: Optional[Literal['v1', 'v2']] = version

    async def _get_full_version(self) -> str:
        res = await self.run_script(_version_detection_script)
        version = res.strip()
        assert re.match(r'^\d+\.', version)
        return version

    async def _get_major_version(self) -> Literal['v1', 'v2']:
        version = await self._get_full_version()
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

    def on_clipboard_change(
        self, callback: Callable[[int], Any], ex_handler: Optional[Callable[[int, Exception], Any]] = None
    ) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        self._hotkey_transport.on_clipboard_change(callback, ex_handler)
        return None

    def add_hotkey(self, hotkey: Hotkey) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._hotkey_transport.add_hotkey(hotkey=hotkey)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    def add_hotstring(self, hotstring: Hotstring) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._hotkey_transport.add_hotstring(hotstring=hotstring)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    def remove_hotkey(self, hotkey: Hotkey) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        self._hotkey_transport.remove_hotkey(hotkey)
        return None

    def clear_hotkeys(self) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        self._hotkey_transport.clear_hotkeys()
        return None

    def remove_hotstring(self, hotstring: Hotstring) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        self._hotkey_transport.remove_hotstring(hotstring)
        return None

    def clear_hotstrings(self) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        self._hotkey_transport.clear_hotstrings()
        return None

    def start_hotkeys(self) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        return self._hotkey_transport.start()

    def stop_hotkeys(self) -> None:
        assert self._hotkey_transport is not None, 'current transport does not support hotkey functionality'
        return self._hotkey_transport.stop()

    async def init(self) -> None:
        self._started = True
        return None

    # fmt: off
    @overload
    async def run_script(self, script_text_or_path: str, /, *, timeout: Optional[int] = None) -> str: ...
    @overload
    async def run_script(self, script_text_or_path: str, /, *, blocking: Literal[False], timeout: Optional[int] = None) -> AsyncFutureResult[str]: ...
    @overload
    async def run_script(self, script_text_or_path: str, /, *, blocking: Literal[True], timeout: Optional[int] = None) -> str: ...
    @overload
    async def run_script(self, script_text_or_path: str, /, *, blocking: bool = True, timeout: Optional[int] = None) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    @abstractmethod
    async def run_script(
        self, script_text_or_path: str, /, *, blocking: bool = True, timeout: Optional[int] = None
    ) -> Union[str, AsyncFutureResult[str]]: ...

    # fmt: off
    @overload
    async def function_call(self, function_name: Literal['AHKWinExist'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKImageSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Coordinates, None, AsyncFutureResult[Union[Coordinates, None]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKPixelGetColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKPixelSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Optional[Coordinates], AsyncFutureResult[Optional[Coordinates]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMouseGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Coordinates, AsyncFutureResult[Coordinates]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKKeyState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[int, float, str, None, AsyncFutureResult[None], AsyncFutureResult[str], AsyncFutureResult[int], AsyncFutureResult[float]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMouseMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKClick'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMouseClickDrag'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKKeyWait'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['SetKeyDelay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendRaw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendInput'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendEvent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSendPlay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetCapsLockState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetNumLockState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetScrollLockState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetClass'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetText'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinActivate'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['WinActivateBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinClose'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinKill'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinMaximize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinMinimize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinRestore'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWindowList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKControlSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinFromMouse'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Optional[AsyncWindow], AsyncFutureResult[Optional[AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinIsAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Optional[bool], AsyncFutureResult[Optional[bool]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[Position, None], AsyncFutureResult[Union[None, Position]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, AsyncWindow], AsyncFutureResult[Union[None, AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetIDLast'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, AsyncWindow], AsyncFutureResult[Union[None, AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetPID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[int, None], AsyncFutureResult[Union[int, None]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetProcessName'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetProcessPath'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetCount'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[int, AsyncFutureResult[int]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetMinMax'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, int], AsyncFutureResult[Union[None, int]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetControlList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[List[AsyncControl], None, AsyncFutureResult[Union[List[AsyncControl], None]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, int], AsyncFutureResult[Union[None, int]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinGetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[Union[None, str], AsyncFutureResult[Union[None, str]]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetDisable'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetEnable'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetRedraw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetRegion'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinSetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
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
    async def function_call(self, function_name: Literal['AHKControlGetText'], args: Optional[List[str]] = None, *, engine: Optional[AsyncAHK[Any]] = None, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKControlClick'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKControlGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[Position, AsyncFutureResult[Position]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetCoordMode'], args: List[str]) -> str: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetCoordMode'], args: List[str]) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetSendLevel']) -> int: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetSendMode'], args: List[str]) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetSendMode']) -> str: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetSendLevel'], args: List[str]) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinWait'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinWaitActive'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinWaitNotActive'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...

    @overload
    async def function_call(self, function_name: Literal['AHKWinShow'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinHide'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinIsActive'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[bool, AsyncFutureResult[bool]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetVolume'], args: Optional[List[str]] = None) -> float: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSoundBeep'], args: Optional[List[str]] = None, *, blocking: bool = True) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSoundGet'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSoundPlay'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSoundSet'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetVolume'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKTrayTip'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetClipboard'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGetClipboardAll'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[bytes, AsyncFutureResult[bytes]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetClipboard'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKSetClipboardAll'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKBlockInput'], args: Optional[List[str]], *, blocking: bool = True) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKShowToolTip'], args: Optional[List[str]]) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKClipWait'], args: Optional[List[str]], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    # @overload
    # async def function_call(self, function_name: Literal['HideTrayTip'], args: Optional[List[str]] = None) -> None: ...
    @overload
    async def function_call(self, function_name: Literal['AHKWinWaitClose'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK[Any]] = None) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKRegRead'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKRegWrite'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKRegDelete'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMenuTrayTip'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMenuTrayIcon'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMenuTrayShow'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMenuTrayHide'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKGuiNew'], args: List[str], *, engine: AsyncAHK[Any]) -> str: ...
    @overload
    async def function_call(self, function_name: Literal['AHKMsgBox'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKInputBox'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKFileSelectFile'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    @overload
    async def function_call(self, function_name: Literal['AHKFileSelectFolder'], args: Optional[List[str]] = None, *, blocking: bool = True) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    # fmt: on

    async def function_call(
        self,
        function_name: FunctionName,
        args: Optional[List[str]] = None,
        blocking: bool = True,
        engine: Optional[AsyncAHK[Any]] = None,
    ) -> Any:
        if not self._started and blocking:
            with warnings.catch_warnings(record=True) as caught_warnings:
                await self.init()
            if caught_warnings:
                for warning in caught_warnings:
                    warnings.warn(warning.message, warning.category, stacklevel=3)
        request = RequestMessage(function_name=function_name, args=args)
        if blocking:
            return await self.send(request, engine=engine)
        else:
            return await self.a_send_nonblocking(request, engine=engine)

    @abstractmethod
    async def send(
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]: ...

    @abstractmethod  # unasync: remove
    async def a_send_nonblocking(  # unasync: remove
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
    ) -> AsyncFutureResult[
        Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]
    ]: ...

    @abstractmethod
    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
    ) -> FutureResult[
        Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]
    ]: ...


class AsyncDaemonProcessTransport(AsyncTransport):
    def __init__(
        self,
        *,
        executable_path: str = '',
        directives: Optional[list[Directive | Type[Directive]]] = None,
        jinja_loader: Optional[jinja2.BaseLoader] = None,
        template: Optional[jinja2.Template] = None,
        extensions: list[Extension] | None = None,
        version: Optional[Literal['v1', 'v2']] = None,
        skip_version_check: bool = False,
    ):
        self._extensions = extensions or []
        self._proc: Optional[AsyncAHKProcess]
        self._proc = None
        self._temp_script: Optional[str] = None
        self.__template: jinja2.Template
        self._jinja_env: jinja2.Environment
        self._execution_lock = threading.Lock()
        self._a_execution_lock = asyncio.Lock()  # unasync: remove
        self._executable_path = executable_path

        if version is None or version == 'v1':
            template_name = 'daemon.ahk'
            const_script = _DAEMON_SCRIPT_TEMPLATE
        elif version == 'v2':
            template_name = 'daemon-v2.ahk'
            const_script = _DAEMON_SCRIPT_V2_TEMPLATE
        else:
            raise ValueError(f'Invalid version {version!r} - must be one of "v1" or "v2"')

        if jinja_loader is None:
            try:
                loader: jinja2.BaseLoader
                loader = jinja2.PackageLoader('ahk', 'templates')
            except ValueError:
                # see: https://github.com/spyoungtech/ahk/issues/201
                warnings.warn(
                    'Jinja could not find templates with PackageLoader. Falling back to BaseLoader',
                    category=UserWarning,
                )
                loader = jinja2.BaseLoader()
            self._jinja_env = jinja2.Environment(loader=loader, trim_blocks=True, autoescape=False)
        else:
            self._jinja_env = jinja2.Environment(loader=jinja_loader, trim_blocks=True, autoescape=False)
        try:
            self.__template = self._jinja_env.get_template(template_name)
        except jinja2.TemplateNotFound:
            warnings.warn('daemon template missing. Falling back to constant', category=UserWarning)
            self.__template = self._jinja_env.from_string(const_script)
        if template is None:
            template = self.__template
        self._template: jinja2.Template = template
        directives = directives or []
        if extensions:
            includes = _resolve_includes(extensions)
            directives = includes + directives
        hotkey_transport = ThreadedHotkeyTransport(
            executable_path=self._executable_path, directives=directives, version=version
        )
        super().__init__(directives=directives, version=version, hotkey_transport=hotkey_transport)

    @property
    def template(self) -> jinja2.Template:
        return self._template

    async def init(self) -> None:
        await self.start()
        await super().init()
        return None

    async def start(self) -> None:
        assert self._proc is None, 'cannot start a process twice'
        with warnings.catch_warnings(record=True) as caught_warnings:
            async with self.lock:
                self._proc = self._create_process()
                await self._proc.start()
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)

    def _render_script(self, template: Optional[jinja2.Template] = None, **kwargs: Any) -> str:
        if template is None:
            template = self._template
        kwargs['daemon'] = self.__template
        message_types = {str(tom, 'utf-8'): c.__name__.upper() for tom, c in _message_registry.items()}
        return template.render(
            directives=self._directives,
            message_types=message_types,
            message_registry=_message_registry,
            extensions=self._extensions,
            ahk_version=self._version,
            **kwargs,
        )

    @property
    def lock(self) -> Any:
        return self._a_execution_lock  # unasync: remove
        return self._execution_lock

    def _create_process(self, template: Optional[jinja2.Template] = None, **template_kwargs: Any) -> AsyncAHKProcess:
        if template is None:
            if template_kwargs:
                raise ValueError('template kwargs were specified, but no template was provided')
            if self._temp_script is None or not os.path.exists(self._temp_script):
                script_text = self._render_script()
                with tempfile.NamedTemporaryFile(
                    mode='w', prefix='python-ahk-', suffix='.ahk', delete=False
                ) as tempscriptfile:
                    tempscriptfile.write(script_text)  # XXX: can we make this async?
                self._temp_script = tempscriptfile.name
                daemon_script = self._temp_script
                atexit.register(try_remove, tempscriptfile.name)
            else:
                daemon_script = self._temp_script
        else:
            script_text = self._render_script(template=template, **template_kwargs)
            with tempfile.NamedTemporaryFile(mode='w', prefix='python-ahk-', suffix='.ahk', delete=False) as tempscript:
                tempscript.write(script_text)
            daemon_script = tempscript.name
            atexit.register(try_remove, tempscript.name)
        runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', daemon_script]
        proc = AsyncAHKProcess(runargs=runargs)
        return proc

    async def _send_nonblocking(
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]:
        msg = request.format()
        async with self._create_process() as proc:
            proc.write(msg)
            await proc.adrain_stdin()
            tom = await proc.readline()
            num_lines = await proc.readline()
            content_buffer = BytesIO()
            content_buffer.write(tom)
            content_buffer.write(num_lines)
            try:
                lines_to_read = int(num_lines) + 1
            except ValueError as e:
                try:
                    stdout = tom + num_lines + await proc.read()
                except Exception:
                    stdout = b''
                raise AHKProtocolError(
                    'Unexpected data received. This is usually the result of an unhandled error in the AHK process'
                    + (f': {stdout!r}' if stdout else '')
                ) from e
            for _ in range(lines_to_read):
                part = await proc.readline()
                content_buffer.write(part)
            content = content_buffer.getvalue()[:-1]
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore

    async def a_send_nonblocking(  # unasync: remove
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
    ) -> AsyncFutureResult[
        Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]
    ]:
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._send_nonblocking(request=request, engine=engine))
        return AsyncFutureResult(task)

    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
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
        self, request: RequestMessage, engine: Optional[AsyncAHK[Any]] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, AsyncWindow, List[AsyncWindow], List[AsyncControl]]:
        msg = request.format()
        assert self._proc is not None
        async with self.lock:
            self._proc.write(msg)
            await self._proc.adrain_stdin()
            tom = await self._proc.readline()
            num_lines = await self._proc.readline()
            content_buffer = BytesIO()
            content_buffer.write(tom)
            content_buffer.write(num_lines)
            try:
                lines_to_read = int(num_lines) + 1
            except ValueError as e:
                try:
                    stdout = tom + num_lines + await self._proc.read()
                except Exception:
                    stdout = b''
                raise AHKProtocolError(
                    'Unexpected data received. This is usually the result of an unhandled error in the AHK process'
                    + (f': {stdout!r}' if stdout else '')
                ) from e
            for _ in range(lines_to_read):
                part = await self._proc.readline()
                content_buffer.write(part)
            content = content_buffer.getvalue()[:-1]
            response = ResponseMessage.from_bytes(content, engine=engine)
            return response.unpack()  # type: ignore

    async def _async_run_nonblocking(  # unasync: remove
        self, proc: Communicable, script_bytes: Optional[bytes], timeout: Optional[int] = None
    ) -> AsyncFutureResult[str]:
        loop = asyncio.get_running_loop()

        async def f() -> str:
            try:
                await proc.start(atexit_cleanup=False)
                stdout, stderr = await proc.acommunicate(script_bytes, timeout)
            finally:
                try:
                    proc.kill()
                except Exception:
                    pass
            if proc.returncode != 0:
                assert proc.returncode is not None
                raise subprocess.CalledProcessError(proc.returncode, proc.runargs, stdout, stderr)
            return stdout.decode('utf-8')

        task = loop.create_task(f())
        return AsyncFutureResult(task)

    def _sync_run_nonblocking(
        self,
        proc: Communicable,
        script_bytes: Optional[bytes],
        timeout: Optional[int] = None,
    ) -> FutureResult[str]:
        raise RuntimeError('This method can only be called from the sync API')  # unasync: remove

        def f() -> str:
            try:
                proc.astart(atexit_cleanup=False)
                stdout, stderr = proc.communicate(script_bytes, timeout)
            finally:
                try:
                    proc.kill()
                except Exception:
                    pass
            if proc.returncode != 0:
                assert proc.returncode is not None
                raise subprocess.CalledProcessError(proc.returncode, proc.runargs, stdout, stderr)
            return stdout.decode('utf-8')

        pool = ThreadPoolExecutor(max_workers=1)
        fut = pool.submit(f)
        pool.shutdown(wait=False)
        return FutureResult(fut)

    # fmt: off
    @overload
    async def run_script(self, script_text_or_path: str, /, *, timeout: Optional[int] = None) -> str: ...
    @overload
    async def run_script(self, script_text_or_path: str, /, *, blocking: Literal[False], timeout: Optional[int] = None) -> AsyncFutureResult[str]: ...
    @overload
    async def run_script(self, script_text_or_path: str, /, *, blocking: Literal[True], timeout: Optional[int] = None) -> str: ...
    @overload
    async def run_script(self, script_text_or_path: str, /, *, blocking: bool = True, timeout: Optional[int] = None) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def run_script(
        self, script_text_or_path: str, /, *, blocking: bool = True, timeout: Optional[int] = None
    ) -> Union[str, AsyncFutureResult[str]]:
        if os.path.exists(script_text_or_path):
            script_bytes = None
            runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', script_text_or_path]
        else:
            script_bytes = bytes(script_text_or_path, 'utf-8')
            runargs = [self._executable_path, '/CP65001', '/ErrorStdOut', '*']
        proc = AsyncAHKProcess(runargs)
        if blocking:
            async with proc:
                stdout, stderr = await proc.acommunicate(script_bytes, timeout=timeout)
                if proc.returncode != 0:
                    assert proc.returncode is not None
                    raise subprocess.CalledProcessError(proc.returncode, proc.runargs, stdout, stderr)
                return stdout.decode('utf-8')
        else:
            return await self._async_run_nonblocking(proc, script_bytes, timeout=timeout)


if TYPE_CHECKING:
    from .engine import AsyncAHK
