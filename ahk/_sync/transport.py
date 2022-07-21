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
from typing import Coroutine
from typing import List
from typing import Literal
from typing import Optional
from typing import overload
from typing import Protocol
from typing import runtime_checkable
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from ahk import SyncControl
    from ahk import Window

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias, TypeGuard
else:
    from typing import TypeAlias, TypeGuard

from ahk.hotkey import ThreadedHotkeyTransport
from concurrent.futures import Future, ThreadPoolExecutor

DEFAULT_EXECUTABLE_PATH = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'



SyncIOProcess: TypeAlias = 'subprocess.Popen[bytes]'


SyncFutureResult: TypeAlias = Future

FunctionName = Literal[
    Literal['AHKWinExist'],
    Literal['ImageSearch'],
    Literal['PixelGetColor'],
    Literal['PixelSearch'],
    Literal['MouseGetPos'],
    Literal['AHKKeyState'],
    Literal['MouseMove'],
    Literal['CoordMode'],
    Literal['Click'],
    Literal['MouseClickDrag'],
    Literal['KeyWait'],
    Literal['SetKeyDelay'],
    Literal['Send'],
    Literal['SendRaw'],
    Literal['SendInput'],
    Literal['SendEvent'],
    Literal['SendPlay'],
    Literal['SetCapsLockState'],
    Literal['WinGetTitle'],
    Literal['WinGetClass'],
    Literal['WinGetText'],
    Literal['WinActivate'],
    Literal['WinActivateBottom'],
    Literal['AHKWinClose'],
    Literal['WinHide'],
    Literal['WinKill'],
    Literal['WinMaximize'],
    Literal['WinMinimize'],
    Literal['WinRestore'],
    Literal['WinShow'],
    Literal['WindowList'],
    Literal['WinSend'],
    Literal['WinSendRaw'],
    Literal['ControlSend'],
    Literal['FromMouse'],
    Literal['WinGet'],
    Literal['WinSet'],
    Literal['WinSetTitle'],
    Literal['WinIsAlwaysOnTop'],
    Literal['WinClick'],
    Literal['AHKWinMove'],
    Literal['AHKWinGetPos'],
    Literal['AHKWinGetID'],
    Literal['AHKWinGetIDLast'],
    Literal['AHKWinGetPID'],
    Literal['AHKWinGetProcessName'],
    Literal['AHKWinGetProcessPath'],
    Literal['AHKWinGetCount'],
    Literal['AHKWinGetList'],
    Literal['AHKWinGetMinMax'],
    Literal['AHKWinGetControlList'],
    Literal['AHKWinGetControlListHwnd'],
    Literal['AHKWinGetTransparent'],
    Literal['AHKWinGetTransColor'],
    Literal['AHKWinGetStyle'],
    Literal['AHKWinGetExStyle'],
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
    Future[Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[SyncControl]]]
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
        assert self._proc is not None
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

    def add_hotkey(
        self, hotkey: str, callback: Callable[[], Any], ex_handler: Optional[Callable[[str, Exception], Any]] = None
    ) -> None:
        return self._hotkey_transport.add_hotkey(hotkey=hotkey, callback=callback, ex_handler=ex_handler)

    def add_hotstring(self, trigger_string: str, replacement: str) -> None:
        return self._hotkey_transport.add_hotstring(trigger_string=trigger_string, replacement=replacement)

    def start_hotkeys(self) -> None:
        return self._hotkey_transport.start()

    def stop_hotkeys(self) -> None:
        return self._hotkey_transport.stop()

    def init(self) -> None:
        self._started = True
        return None

    # fmt: off
    @overload
    def function_call(self, function_name: Literal['AHKWinExist'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, SyncFutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['ImageSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Tuple[int, int], None, SyncFutureResult[Union[Tuple[int, int], None]]]: ...
    @overload
    def function_call(self, function_name: Literal['PixelGetColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, SyncFutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['PixelSearch'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Tuple[int, int], SyncFutureResult[Tuple[int, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['MouseGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Tuple[int, int], SyncFutureResult[Tuple[int, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKKeyState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, SyncFutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['MouseMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['CoordMode'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['Click'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['MouseClickDrag'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['KeyWait'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[int, SyncFutureResult[int]]: ...
    @overload
    def function_call(self, function_name: Literal['SetKeyDelay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['Send'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['SendRaw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['SendInput'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['SendEvent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['SendPlay'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['SetCapsLockState'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinGetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, SyncFutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['WinGetClass'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, SyncFutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['WinGetText'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, SyncFutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['WinActivate'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinActivateBottom'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinClose'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinHide'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinKill'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinMaximize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinMinimize'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinRestore'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinShow'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WindowList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[List[Window], SyncFutureResult[List[Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['WinSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinSendRaw'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['ControlSend'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['FromMouse'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, SyncFutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['WinGet'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[str, SyncFutureResult[str]]: ...
    @overload
    def function_call(self, function_name: Literal['WinSet'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinSetTitle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['WinIsAlwaysOnTop'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[bool, SyncFutureResult[bool]]: ...
    @overload
    def function_call(self, function_name: Literal['WinClick'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinMove'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[None, SyncFutureResult[None]]: ...
    # @overload
    # async def function_call(self, function_name: Literal['AHKWinGetPos'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK) = None -> Union[TupleResponseMessage, AsyncFutureResult[TupleResponseMessage]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, Window], SyncFutureResult[Union[None, Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetIDLast'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, Window], SyncFutureResult[Union[None, Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetPID'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[int, None], SyncFutureResult[Union[int, None]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetProcessName'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], SyncFutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetProcessPath'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], SyncFutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetCount'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[int, SyncFutureResult[int]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[List[Window], SyncFutureResult[List[Window]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetMinMax'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, int], SyncFutureResult[Union[None, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetControlList'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[List[SyncControl], None, SyncFutureResult[Union[List[SyncControl], None]]]: ...
    # @overload
    # async def function_call(self, function_name: Literal['AHKWinGetControlListHwnd'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AsyncAHK] = None) -> Union[List[AsyncControl], AsyncFutureResult[List[AsyncControl]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetTransparent'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, int], SyncFutureResult[Union[None, int]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetTransColor'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], SyncFutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], SyncFutureResult[Union[None, str]]]: ...
    @overload
    def function_call(self, function_name: Literal['AHKWinGetExStyle'], args: Optional[List[str]] = None, *, blocking: bool = True, engine: Optional[AHK] = None) -> Union[Union[None, str], SyncFutureResult[Union[None, str]]]: ...

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
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[SyncControl]]:
        return NotImplemented


    @abstractmethod
    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> SyncFutureResult[
        Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[SyncControl]]
    ]:
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
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[SyncControl]]:
        newline = '\n'

        msg = f"{request.function_name}{',' if request.args else ''}{','.join(arg.replace(newline, '`n') for arg in request.args)}\n".encode(
            'utf-8'
        )
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
            except:
                pass
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore


    def send_nonblocking(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> SyncFutureResult[
        Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[SyncControl]]
    ]:
        # this is only used by the sync implementation
        pool = ThreadPoolExecutor(max_workers=1)
        fut = pool.submit(self._send_nonblocking, request=request, engine=engine)
        pool.shutdown(wait=False)
        assert async_assert_send_nonblocking_type_correct(
            fut
        )  # workaround to get mypy correctness in sync and async implementation
        return fut

    def send(
        self, request: RequestMessage, engine: Optional[AHK] = None
    ) -> Union[None, Tuple[int, int], int, str, bool, Window, List[Window], List[SyncControl]]:
        newline = '\n'

        msg = f"{request.function_name}{',' if request.args else ''}{','.join(arg.replace(newline, '`n') for arg in request.args)}\n".encode(
            'utf-8'
        )
        assert self._proc is not None
        self._proc.write(msg)
        self._proc.drain_stdin()
        tom = self._proc.readline()
        num_lines = self._proc.readline()
        content_buffer = BytesIO()
        content_buffer.write(tom)
        content_buffer.write(num_lines)
        for _ in range(int(num_lines) + 1):
            part = self._proc.readline()
            content_buffer.write(part)
        content = content_buffer.getvalue()[:-1]
        response = ResponseMessage.from_bytes(content, engine=engine)
        return response.unpack()  # type: ignore


from ahk.message import RequestMessage
from ahk.message import ResponseMessage


if TYPE_CHECKING:
    from .engine import AHK
    from ahk import AHK
