from __future__ import annotations

from typing import Literal
from typing import Optional
from typing import overload
from typing import Sequence
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from .engine import AsyncAHK
    from .transport import AsyncFutureResult


class WindowNotFoundException(Exception):
    ...


class AsyncWindow:
    def __init__(self, engine: AsyncAHK, ahk_id: str):
        self._engine: AsyncAHK = engine
        if not ahk_id:
            raise ValueError(f'Invalid ahk_id: {ahk_id!r}')
        self._ahk_id: str = ahk_id

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__} ahk_id={self._ahk_id}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncWindow):
            return NotImplemented
        return self._ahk_id == other._ahk_id

    def __hash__(self) -> int:
        return hash(self._ahk_id)

    async def close(self) -> None:
        await self._engine.win_close(title=f'ahk_id {self._ahk_id}')
        return None

    async def exists(self) -> bool:
        return await self._engine.win_exists(title=f'ahk_id {self._ahk_id}')

    async def get_pid(self) -> int:
        pid = await self._engine.win_get_pid(title=f'ahk_id {self._ahk_id}')
        if pid is None:
            raise WindowNotFoundException(
                f'Error when trying to get PID of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return pid

    async def get_process_name(self) -> str:
        name = await self._engine.win_get_process_name(title=f'ahk_id {self._ahk_id}')
        if name is None:
            raise WindowNotFoundException(
                f'Error when trying to get process name of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return name

    async def get_process_path(self) -> str:
        path = await self._engine.win_get_process_path(title=f'ahk_id {self._ahk_id}')
        if path is None:
            raise WindowNotFoundException(
                f'Error when trying to get process path of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return path

    async def get_minmax(self) -> int:
        minmax = await self._engine.win_get_minmax(title=f'ahk_id {self._ahk_id}')
        if minmax is None:
            raise WindowNotFoundException(
                f'Error when trying to get minmax state of window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return minmax

    async def get_title(self) -> str:
        title = await self._engine.win_get_title(title=f'ahk_id {self._ahk_id}')
        return title

    async def list_controls(self) -> Sequence['AsyncControl']:
        controls = await self._engine.win_get_control_list(title=f'ahk_id {self._ahk_id}')
        if controls is None:
            raise WindowNotFoundException(
                f'Error when trying to enumerate controls for window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return controls

    async def set_title(self, new_title: str) -> None:
        await self._engine.win_set_title(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, new_title=new_title
        )
        return None

    # fmt: off
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0]) -> None: ...
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: Literal[True]) -> None: ...
    # fmt: on
    async def set_always_on_top(
        self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        if blocking:
            await self._engine.win_set_always_on_top(toggle=toggle, title=f'ahk_id {self._ahk_id}', blocking=True)
            return None
        else:
            resp = await self._engine.win_set_always_on_top(
                toggle=toggle, title=f'ahk_id {self._ahk_id}', blocking=False
            )
            return resp

    # fmt: off
    @overload
    async def is_always_on_top(self) -> bool: ...
    @overload
    async def is_always_on_top(self, *, blocking: Literal[False]) -> AsyncFutureResult[Optional[bool]]: ...
    @overload
    async def is_always_on_top(self, *, blocking: Literal[True]) -> bool: ...
    # fmt: on
    async def is_always_on_top(self, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[Optional[bool]]]:
        args = [f'ahk_id {self._ahk_id}']
        resp = await self._engine._transport.function_call(
            'AHKWinIsAlwaysOnTop', args, blocking=blocking
        )  # XXX: maybe shouldn't access transport directly?
        if resp is None:
            raise WindowNotFoundException(
                f'Error when trying to get always on top style for window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return resp

    # fmt: off
    @overload
    async def send(self, keys: str) -> None: ...
    @overload
    async def send(self, keys: str, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send(self, keys: str, *, blocking: Literal[True]) -> None: ...
    # fmt: on
    async def send(self, keys: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        if blocking:
            await self._engine.control_send(keys=keys, title=f'ahk_id {self._ahk_id}', blocking=True)
            return None
        else:
            resp = await self._engine.control_send(keys=keys, title=f'ahk_id {self._ahk_id}', blocking=False)
            return resp

    # fmt: off
    @overload
    async def get_text(self) -> str: ...
    @overload
    async def get_text(self, *, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def get_text(self, *, blocking: Literal[True]) -> str: ...
    # fmt: on
    async def get_text(self, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]:
        if blocking:
            resp = await self._engine.win_get_text(title=f'ahk_id {self._ahk_id}', blocking=True)
            return resp
        else:
            nonblocking_resp = await self._engine.win_get_text(title=f'ahk_id {self._ahk_id}', blocking=False)
            return nonblocking_resp


class AsyncControl:
    def __init__(self, window: AsyncWindow, hwnd: str, control_class: str):
        self.window: AsyncWindow = window
        self.hwnd: str = hwnd
        self.control_class: str = control_class

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} window={self.window!r}, control_hwnd={self.hwnd!r}, control_class={self.control_class!r}>'
