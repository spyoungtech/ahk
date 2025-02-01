from __future__ import annotations

import sys
import warnings
from functools import partial
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import Literal
from typing import Optional
from typing import overload
from typing import Sequence
from typing import Tuple
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import TypeVar
from typing import Union

from ahk._types import Position
from ahk.exceptions import WindowNotFoundException

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

if sys.version_info < (3, 11):
    from typing_extensions import NotRequired
else:
    from typing import NotRequired

if TYPE_CHECKING:
    from .engine import AsyncAHK
    from .transport import AsyncFutureResult


AsyncPropertyReturnStr: TypeAlias = Coroutine[None, None, str]  # unasync: remove
SyncPropertyReturnStr: TypeAlias = str

AsyncPropertyReturnInt: TypeAlias = Coroutine[None, None, int]  # unasync: remove
SyncPropertyReturnInt: TypeAlias = int

AsyncPropertyReturnTupleIntInt: TypeAlias = Coroutine[None, None, Tuple[int, int]]  # unasync: remove
SyncPropertyReturnTupleIntInt: TypeAlias = Tuple[int, int]

AsyncPropertyReturnBool: TypeAlias = Coroutine[None, None, bool]  # unasync: remove
SyncPropertyReturnBool: TypeAlias = bool

_PROPERTY_DEPRECATION_WARNING_MESSAGE = 'Use of the {0} property is not recommended (in the async API only) and may be removed in a future version. Use the get_{0} method instead.'
_SETTERS_REMOVED_ERROR_MESSAGE = (
    'Use of the {0} property setter is not supported in the async API. Use the set_{0} instead.'
)

T_EngineVersion = TypeVar('T_EngineVersion', bound=Optional[Literal['v1', 'v2']])


class AsyncWindow:
    def __init__(self, engine: AsyncAHK[T_EngineVersion], ahk_id: str):
        self._engine: AsyncAHK[T_EngineVersion] = engine
        if not ahk_id:
            raise ValueError(f'Invalid ahk_id: {ahk_id!r}')
        self._ahk_id: str = ahk_id

    def __repr__(self) -> str:
        return f'<{self.__class__.__qualname__} ahk_id={self._ahk_id!r}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncWindow):
            return NotImplemented
        return self._ahk_id == other._ahk_id

    def __hash__(self) -> int:
        return hash(self._ahk_id)

    def __getattr__(self, name: str) -> Callable[..., Any]:
        method = self._engine._get_window_extension_method(name)
        if method is None:
            raise AttributeError(f'{self.__class__.__name__!r} object has no attribute {name!r}')
        else:
            return partial(method, self)

    async def close(self) -> None:
        await self._engine.win_close(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        return None

    async def kill(self) -> None:
        await self._engine.win_kill(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )

    async def exists(self) -> bool:
        return await self._engine.win_exists(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )

    @property
    def id(self) -> str:
        return self._ahk_id

    @property
    def exist(self) -> AsyncPropertyReturnBool:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('exist'), category=DeprecationWarning, stacklevel=2
        )
        return self.exists()

    async def get_pid(self) -> int:
        pid = await self._engine.win_get_pid(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        if pid is None:
            raise WindowNotFoundException(
                f'Error when trying to get PID of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return pid

    @property
    def pid(self) -> AsyncPropertyReturnInt:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('pid'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_pid()

    async def get_process_name(self) -> str:
        name = await self._engine.win_get_process_name(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        if name is None:
            raise WindowNotFoundException(
                f'Error when trying to get process name of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return name

    @property
    def process_name(self) -> AsyncPropertyReturnStr:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('process_name'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_process_name()

    async def get_process_path(self) -> str:
        path = await self._engine.win_get_process_path(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        if path is None:
            raise WindowNotFoundException(
                f'Error when trying to get process path of window {self._ahk_id!r}. The window may have been closed before the operation could be completed'
            )
        return path

    @property
    def process_path(self) -> AsyncPropertyReturnStr:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('process_path'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_process_path()

    async def get_minmax(self) -> int:
        minmax = await self._engine.win_get_minmax(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        if minmax is None:
            raise WindowNotFoundException(
                f'Error when trying to get minmax state of window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return minmax

    async def get_title(self) -> str:
        title = await self._engine.win_get_title(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        return title

    @property
    def title(self) -> AsyncPropertyReturnStr:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('title'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_title()

    @title.setter
    def title(self, value: str) -> Any:
        raise RuntimeError(_SETTERS_REMOVED_ERROR_MESSAGE)  # unasync: remove
        self.set_title(value)

    async def set_title(self, new_title: str) -> None:
        await self._engine.win_set_title(
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            new_title=new_title,
            title_match_mode=(1, 'Fast'),
        )
        return None

    async def list_controls(self) -> Sequence['AsyncControl']:
        controls = await self._engine.win_get_control_list(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )
        if controls is None:
            raise WindowNotFoundException(
                f'Error when trying to enumerate controls for window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return controls

    # fmt: off
    @overload
    async def minimize(self) -> None: ...
    @overload
    async def minimize(self, blocking: Literal[True]) -> None: ...
    @overload
    async def minimize(self, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def minimize(self, blocking: bool = True) -> Optional[AsyncFutureResult[None]]: ...
    # fmt: on
    async def minimize(self, blocking: bool = True) -> Optional[AsyncFutureResult[None]]:
        return await self._engine.win_minimize(
            title=f'ahk_id {self._ahk_id}', title_match_mode=(1, 'Fast'), detect_hidden_windows=True, blocking=blocking
        )

    # fmt: off
    @overload
    async def maximize(self) -> None: ...
    @overload
    async def maximize(self, blocking: Literal[True]) -> None: ...
    @overload
    async def maximize(self, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def maximize(self, blocking: bool = True) -> Optional[AsyncFutureResult[None]]: ...
    # fmt: on
    async def maximize(self, blocking: bool = True) -> Optional[AsyncFutureResult[None]]:
        return await self._engine.win_maximize(
            title=f'ahk_id {self._ahk_id}', title_match_mode=(1, 'Fast'), detect_hidden_windows=True, blocking=blocking
        )

    # fmt: off
    @overload
    async def restore(self) -> None: ...
    @overload
    async def restore(self, blocking: Literal[True]) -> None: ...
    @overload
    async def restore(self, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def restore(self, blocking: bool = True) -> Optional[AsyncFutureResult[None]]: ...
    # fmt: on
    async def restore(self, blocking: bool = True) -> Optional[AsyncFutureResult[None]]:
        return await self._engine.win_restore(
            title=f'ahk_id {self._ahk_id}', title_match_mode=(1, 'Fast'), detect_hidden_windows=True, blocking=blocking
        )

    # fmt: off
    @overload
    async def get_class(self) -> str: ...
    @overload
    async def get_class(self, blocking: Literal[True]) -> str: ...
    @overload
    async def get_class(self, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def get_class(self, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def get_class(self, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]:
        return await self._engine.win_get_class(
            title=f'ahk_id {self._ahk_id}', detect_hidden_windows=True, title_match_mode=(1, 'Fast'), blocking=blocking
        )

    # fmt: off
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0]) -> None: ...
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_always_on_top(
        self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_always_on_top(
            toggle=toggle,
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def is_always_on_top(self) -> bool: ...
    @overload
    async def is_always_on_top(self, *, blocking: Literal[False]) -> AsyncFutureResult[Optional[bool]]: ...
    @overload
    async def is_always_on_top(self, *, blocking: Literal[True]) -> bool: ...
    @overload
    async def is_always_on_top(self, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[Optional[bool]]]: ...
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

    @property
    def always_on_top(self) -> AsyncPropertyReturnBool:
        return self.is_always_on_top()

    @always_on_top.setter
    def always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0]) -> Any:
        raise RuntimeError(_SETTERS_REMOVED_ERROR_MESSAGE)  # unasync: remove
        self.set_always_on_top(toggle)

    # fmt: off
    @overload
    async def send(self, keys: str, control: str = '') -> None: ...
    @overload
    async def send(self, keys: str, control: str = '', *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send(self, keys: str, control: str = '', *, blocking: Literal[True]) -> None: ...
    @overload
    async def send(self, keys: str, control: str = '', *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send(
        self, keys: str, control: str = '', *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.control_send(
            keys=keys,
            control=control,
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def click(self, x: int = 0, y: int = 0, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '') -> None: ...
    @overload
    async def click(self, x: int = 0, y: int = 0, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def click(self, x: int = 0, y: int = 0, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', blocking: Literal[True]) -> None: ...
    @overload
    async def click(self, x: int = 0, y: int = 0, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def click(
        self,
        x: int = 0,
        y: int = 0,
        *,
        button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L',
        click_count: int = 1,
        options: str = '',
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        pos = f'X{x} Y{y}'
        return await self._engine.control_click(
            control=pos,
            title=f'ahk_id {self._ahk_id}',
            button=button,
            click_count=click_count,
            options=options,
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def get_text(self) -> str: ...
    @overload
    async def get_text(self, *, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def get_text(self, *, blocking: Literal[True]) -> str: ...
    @overload
    async def get_text(self, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def get_text(self, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]:
        return await self._engine.win_get_text(
            title=f'ahk_id {self._ahk_id}', blocking=blocking, detect_hidden_windows=True, title_match_mode=(1, 'Fast')
        )

    @property
    def text(self) -> AsyncPropertyReturnStr:
        return self.get_text()

    # fmt: off
    @overload
    async def get_position(self) -> Position: ...
    @overload
    async def get_position(self, *, blocking: Literal[False]) -> AsyncFutureResult[Optional[Position]]: ...
    @overload
    async def get_position(self, *, blocking: Literal[True]) -> Position: ...
    @overload
    async def get_position(self, *, blocking: bool = True) -> Union[Position, AsyncFutureResult[Optional[Position]], AsyncFutureResult[Position]]: ...
    # fmt: on
    async def get_position(
        self, *, blocking: bool = True
    ) -> Union[Position, AsyncFutureResult[Optional[Position]], AsyncFutureResult[Position]]:
        resp = await self._engine.win_get_position(  # type: ignore[misc] # this appears to be a mypy bug
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )
        if resp is None:
            raise WindowNotFoundException(
                f'Error when trying to get position for window {self._ahk_id}. The window may have been closed before the operation could be completed'
            )
        return resp

    # fmt: off
    @overload
    async def activate(self) -> None: ...
    @overload
    async def activate(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def activate(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def activate(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def activate(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        resp = await self._engine.win_activate(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )
        return resp

    # fmt: off
    @overload
    async def to_bottom(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def to_bottom(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def to_bottom(self) -> None: ...
    # fmt: on
    async def to_bottom(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_bottom(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def to_top(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def to_top(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def to_top(self) -> None: ...
    # fmt: on
    async def to_top(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_top(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def show(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def show(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show(self) -> None: ...
    # fmt: on
    async def show(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_show(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def hide(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def hide(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def hide(self) -> None: ...
    # fmt: on
    async def hide(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_hide(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def disable(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def disable(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def disable(self) -> None: ...
    # fmt: on
    async def disable(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_disable(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def enable(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def enable(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def enable(self) -> None: ...
    # fmt: on
    async def enable(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_enable(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    # fmt: off
    @overload
    async def redraw(self, *, blocking: Literal[True]) -> None: ...
    @overload
    async def redraw(self, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def redraw(self) -> None: ...
    @overload
    async def redraw(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def redraw(self, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_redraw(
            title=f'ahk_id {self._ahk_id}',
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    @overload
    async def set_style(self, style: str) -> bool: ...

    @overload
    async def set_style(self, style: str, *, blocking: Literal[True]) -> bool: ...

    @overload
    async def set_style(self, style: str, *, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...

    @overload
    async def set_style(self, style: str, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...

    async def set_style(self, style: str, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]:
        return await self._engine.win_set_style(
            style=style,
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            blocking=blocking,
        )

    @overload
    async def set_ex_style(self, style: str) -> bool: ...

    @overload
    async def set_ex_style(self, style: str, *, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...

    @overload
    async def set_ex_style(self, style: str, *, blocking: Literal[True]) -> bool: ...

    @overload
    async def set_ex_style(self, style: str, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...

    async def set_ex_style(self, style: str, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]:
        return await self._engine.win_set_ex_style(
            style=style,
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            blocking=blocking,
        )

    @overload
    async def set_region(self, options: str) -> bool: ...

    @overload
    async def set_region(self, options: str, *, blocking: Literal[True]) -> bool: ...

    @overload
    async def set_region(self, options: str, *, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...

    @overload
    async def set_region(self, options: str, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...

    async def set_region(self, options: str, *, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]:
        return await self._engine.win_set_region(
            options=options,
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            blocking=blocking,
        )

    async def set_transparent(
        self, transparency: Union[int, Literal['Off']], *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_transparent(
            transparency=transparency,
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            blocking=blocking,
        )

    async def set_trans_color(
        self, color: Union[int, str], *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_set_trans_color(
            color=color,
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            blocking=blocking,
        )

    @property
    def active(self) -> AsyncPropertyReturnBool:
        return self.is_active()

    async def is_active(self) -> bool:
        return await self._engine.win_is_active(
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
        )

    async def move(
        self, x: int, y: int, *, width: Optional[int] = None, height: Optional[int] = None, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.win_move(
            x=x,
            y=y,
            width=width,
            height=height,
            title=f'ahk_id {self._ahk_id}',
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            blocking=blocking,
        )

    # fmt: off
    @overload
    @classmethod
    async def from_pid(cls, engine: AsyncAHK[Literal['v2']], pid: int) -> AsyncWindow: ...
    @overload
    @classmethod
    async def from_pid(cls, engine: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], pid: int) -> Optional[AsyncWindow]: ...
    # fmt: on
    @classmethod
    async def from_pid(cls, engine: AsyncAHK[Any], pid: int) -> Optional[AsyncWindow]:
        return await engine.win_get(title=f'ahk_pid {pid}')

    @classmethod
    async def from_mouse_position(cls, engine: AsyncAHK[Any]) -> Optional[AsyncWindow]:
        return await engine.win_get_from_mouse_position()


_ControlTargetKwargs = TypedDict('_ControlTargetKwargs', {'title': str, 'control': NotRequired[str]})


class AsyncControl:
    def __init__(self, window: AsyncWindow, hwnd: str, control_class: str):
        self.window: AsyncWindow = window
        self.hwnd: str = hwnd
        self.control_class: str = control_class
        self._engine = window._engine
        self.use_hwnd: bool = False

    def _get_target_params(self, use_hwnd: Optional[bool] = None) -> _ControlTargetKwargs:
        if use_hwnd is None:
            use_hwnd = self.use_hwnd
        if use_hwnd:
            return {'title': f'ahk_id {self.hwnd}'}
        else:
            return {'title': f'ahk_id {self.window._ahk_id}', 'control': self.control_class}

    # fmt: off
    @overload
    async def click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', use_hwnd: Optional[bool] = None) -> None: ...
    @overload
    async def click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', use_hwnd: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', use_hwnd: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', use_hwnd: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def click(
        self,
        *,
        button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L',
        click_count: int = 1,
        options: str = '',
        use_hwnd: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.control_click(
            button=button,
            click_count=click_count,
            options=options,
            title_match_mode=(1, 'Fast'),
            detect_hidden_windows=True,
            blocking=blocking,
            **self._get_target_params(use_hwnd),
        )

    # fmt: off
    @overload
    async def send(self, keys: str, *, use_hwnd: Optional[bool] = None) -> None: ...
    @overload
    async def send(self, keys: str, *, use_hwnd: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send(self, keys: str, *, use_hwnd: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def send(self, keys: str, *, use_hwnd: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send(
        self, keys: str, *, use_hwnd: Optional[bool] = None, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        return await self._engine.control_send(
            keys=keys,
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            **self._get_target_params(use_hwnd),
        )

    async def get_text(
        self, *, use_hwnd: Optional[bool] = None, blocking: bool = True
    ) -> Union[str, AsyncFutureResult[str]]:
        return await self._engine.control_get_text(
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            **self._get_target_params(use_hwnd),
        )

    # fmt: off
    @overload
    async def get_position(self, *, use_hwnd: Optional[bool] = None) -> Position: ...
    @overload
    async def get_position(self, *, use_hwnd: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Position]: ...
    @overload
    async def get_position(self, *, use_hwnd: Optional[bool] = None, blocking: Literal[True]) -> Position: ...
    @overload
    async def get_position(self, *, use_hwnd: Optional[bool] = None, blocking: bool = True) -> Union[Position, AsyncFutureResult[Position]]: ...
    # fmt: on
    async def get_position(
        self, *, use_hwnd: Optional[bool] = None, blocking: bool = True
    ) -> Union[Position, AsyncFutureResult[Position]]:
        return await self._engine.control_get_position(
            blocking=blocking,
            detect_hidden_windows=True,
            title_match_mode=(1, 'Fast'),
            **self._get_target_params(use_hwnd),
        )

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} window={self.window!r}, control_hwnd={self.hwnd!r}, control_class={self.control_class!r}>'
