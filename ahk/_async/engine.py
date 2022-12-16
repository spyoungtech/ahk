from __future__ import annotations

import asyncio
import sys
import time
import warnings
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Coroutine
from typing import Dict
from typing import List
from typing import Literal
from typing import NoReturn
from typing import Optional
from typing import overload
from typing import Tuple
from typing import Type
from typing import Union

from .._hotkey import Hotkey
from .._hotkey import Hotstring

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

from ..keys import Key
from .transport import AsyncDaemonProcessTransport
from .transport import AsyncFutureResult
from .transport import AsyncTransport
from .window import AsyncControl
from .window import AsyncWindow
from ahk.message import Position

async_sleep = asyncio.sleep  # unasync: remove
sleep = time.sleep

AsyncFilterFunc: TypeAlias = Callable[[AsyncWindow], Awaitable[bool]]  # unasync: remove
SyncFilterFunc: TypeAlias = Callable[[AsyncWindow], bool]

CoordModeTargets: TypeAlias = Union[
    Literal['ToolTip'], Literal['Pixel'], Literal['Mouse'], Literal['Caret'], Literal['Menu']
]
CoordModeRelativeTo: TypeAlias = Union[Literal['Screen', 'Relative', 'Window', 'Client', '']]

CoordMode: TypeAlias = Union[CoordModeTargets, Tuple[CoordModeTargets, CoordModeRelativeTo]]

MatchModes: TypeAlias = Literal[1, 2, 3, 'RegEx', '']
MatchSpeeds: TypeAlias = Literal['Fast', 'Slow', '']

TitleMatchMode: TypeAlias = Optional[
    Union[MatchModes, MatchSpeeds, Tuple[Union[MatchModes, MatchSpeeds], Union[MatchSpeeds, MatchModes]]]
]

_BUTTONS: dict[Union[str, int], str] = {
    1: 'L',
    2: 'R',
    3: 'M',
    'left': 'L',
    'right': 'R',
    'middle': 'M',
    'wheelup': 'WU',
    'wheeldown': 'WD',
    'wheelleft': 'WL',
    'wheelright': 'WR',
}

MouseButton: TypeAlias = Union[
    int,
    Literal[
        'L',
        'R',
        'M',
        'left',
        'right',
        'middle',
        'wheelup',
        'WU',
        'wheeldown',
        'WD',
        'wheelleft',
        'WL',
        'wheelright',
        'WR',
    ],
]

AsyncPropertyReturnTupleIntInt: TypeAlias = Coroutine[None, None, Tuple[int, int]]  # unasync: remove
SyncPropertyReturnTupleIntInt: TypeAlias = Tuple[int, int]

AsyncPropertyReturnOptionalAsyncWindow: TypeAlias = Coroutine[None, None, Optional[AsyncWindow]]  # unasync: remove
SyncPropertyReturnOptionalAsyncWindow: TypeAlias = Optional[AsyncWindow]

_PROPERTY_DEPRECATION_WARNING_MESSAGE = 'Use of the {0} property is not recommended (in the async API only) and may be removed in a future version. Use the get_{0} method instead'


def resolve_button(button: Union[str, int]) -> str:
    """
    Resolve a string of a button name to a canonical name used for AHK script
    :param button:
    :type button: str
    :return:
    """
    if isinstance(button, str):
        button = button.lower()

    if button in _BUTTONS:
        resolved_button = _BUTTONS[button]
    elif isinstance(button, int) and button > 3:
        #  for addtional mouse buttons
        resolved_button = f'X{button-3}'
    else:
        assert isinstance(button, str)
        resolved_button = button
    return resolved_button


class AsyncAHK:
    def __init__(
        self,
        *,
        TransportClass: Optional[Type[AsyncTransport]] = None,
        transport_options: Optional[Dict[str, Any]] = None,
    ):
        if transport_options is None:
            transport_options = {}
        if TransportClass is None:
            TransportClass = AsyncDaemonProcessTransport
        assert TransportClass is not None
        transport = TransportClass(**transport_options)
        self._transport: AsyncTransport = transport

    def __getattr__(self, item: Any) -> Any:
        deprecation_replacements: Dict[str, Any] = {'type': self.send_input}
        if item in deprecation_replacements:
            func = deprecation_replacements[item]
            warnings.warn(
                f'{item!r} is deprecated and will be removed in a future version. Use {func.__name__!r} instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            return deprecation_replacements[item]
        raise AttributeError(f'{self.__class__.__qualname__!r} object has no attribute {item!r}')

    def add_hotkey(
        self, keyname: str, callback: Callable[[], Any], *, ex_handler: Optional[Callable[[str, Exception], Any]] = None
    ) -> None:
        """
        Register a function to be called when a hotkey is pressed.

        Key notes:

        - You must call the `start_hotkeys` method for the hotkeys to be active
        - All hotkeys run in a single AHK process instance (but Python callbacks also get their own thread and can run simultaneously)
        - If you add a hotkey after the hotkey thread/instance is active, it will be restarted automatically
        - `async` functions are not directly supported as callbacks, however you may write a synchronous function that calls `asyncio.run`/`loop.create_task` etc.

        :param hotkey: an instance of ahk.hotkey.Hotkey
        """
        hotkey = Hotkey(keyname, callback, ex_handler=ex_handler)
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._transport.add_hotkey(hotkey=hotkey)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    def add_hotstring(
        self,
        trigger: str,
        replacement_or_callback: Union[str, Callable[[], Any]],
        *,
        ex_handler: Optional[Callable[[str, Exception], Any]] = None,
        options: str = '',
    ) -> None:
        """
        Register a hotstring, e.g., `::btw::by the way`

        Key notes:

        - You must call the `start_hotkeys` method for registered hotstrings to be active
        - All hotstrings (and hotkeys) run in a single AHK process instance separate from other AHK processes.

        :param hotstring: an instance of ahk.hotkey.Hotstring
        """
        hotstring = Hotstring(trigger, replacement_or_callback, ex_handler=ex_handler, options=options)
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._transport.add_hotstring(hotstring=hotstring)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    async def set_title_match_mode(self, title_match_mode: TitleMatchMode, /) -> None:
        """
        Sets the default title match mode

        Has no effect for `Window`/`Control` instance methods (these always use hwnd)

        Does not affect methods called with `blocking=True` (because these run in a separate AHK process)

        Reference: https://www.autohotkey.com/docs/commands/SetTitleMatchMode.htm

        :param title_match_mode: the match mode (and/or match speed) to set as the default title match mode. Can be 1, 2, 3, 'Regex', 'Fast', 'Slow' or a tuple of these.
        :return: None
        """

        args = []
        if isinstance(title_match_mode, tuple):
            (match_mode, match_speed) = title_match_mode
        elif title_match_mode in (1, 2, 3, 'RegEx'):
            match_mode = title_match_mode
            match_speed = ''
        elif title_match_mode in ('Fast', 'Slow'):
            match_mode = ''
            match_speed = title_match_mode
        else:
            raise ValueError(
                f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
            )
        args.append(str(match_mode))
        args.append(str(match_speed))
        await self._transport.function_call('AHKSetTitleMatchMode', args)
        return None

    async def get_title_match_mode(self) -> str:
        """
        Get the title match mode.

        I.E. the current value of `A_TitleMatchMode`

        """
        resp = await self._transport.function_call('AHKGetTitleMatchMode')
        return resp

    async def get_title_match_speed(self) -> str:
        """
        Get the title match mode speed.

        I.E. the current value of `A_TitleMatchModeSpeed`

        """
        resp = await self._transport.function_call('AHKGetTitleMatchSpeed')
        return resp

    async def set_coord_mode(self, target: CoordModeTargets, relative_to: CoordModeRelativeTo = 'Screen') -> None:
        args = [str(target), str(relative_to)]
        await self._transport.function_call('AHKSetCoordMode', args)
        return None

    async def get_coord_mode(self, target: CoordModeTargets) -> str:
        args = [str(target)]
        resp = await self._transport.function_call('AHKGetCoordMode', args)
        return resp

    # fmt: off
    @overload
    async def control_click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def control_click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def control_click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def control_click(self, *, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def control_click(
        self,
        *,
        button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L',
        click_count: int = 1,
        options: str = '',
        control: str = '',
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [control, title, text, str(button), str(click_count), options, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKControlClick', args=args, blocking=blocking)

        return resp

    # fmt: off
    @overload
    async def control_get_text(self, *, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> str: ...
    @overload
    async def control_get_text(self, *, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def control_get_text(self, *, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> str: ...
    @overload
    async def control_get_text(self, *, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def control_get_text(
        self,
        *,
        control: str = '',
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        args = [control, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKControlGetText', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def control_get_position(self, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Position: ...
    @overload
    async def control_get_position(self, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Position]: ...
    @overload
    async def control_get_position(self, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Position: ...
    @overload
    async def control_get_position(self, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[Position, AsyncFutureResult[Position]]: ...
    # fmt: on
    async def control_get_position(
        self,
        control: str = '',
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[Position, AsyncFutureResult[Position]]:
        args = [control, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')

        resp = await self._transport.function_call('AHKControlGetPos', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def control_send(self, keys: str, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def control_send(self, keys: str, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def control_send(self, keys: str, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def control_send(self, keys: str, control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def control_send(
        self,
        keys: str,
        control: str = '',
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for ControlSend

        Reference: https://www.autohotkey.com/docs/commands/ControlSend.htm

        :param keys:
        :param control:
        :param title:
        :param text:
        :param exclude_title:
        :param exclude_text:
        :param title_match_mode:
        :param detect_hidden_windows:
        :param blocking:
        :return:
        """
        args = [control, keys, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKControlSend', args, blocking=blocking)
        return resp

    def start_hotkeys(self) -> None:
        """
        Start the Autohotkey process for triggering hotkeys

        """
        return self._transport.start_hotkeys()

    def stop_hotkeys(self) -> None:
        """
        Stop the Autohotkey process for triggering hotkeys

        """
        return self._transport.stop_hotkeys()

    async def set_detect_hidden_windows(self, value: bool) -> None:
        """
        Analog for AutoHotkey's `DetectHiddenWindows`

        :param value: The setting value. `True` to turn on hidden window detection, `False` to turn it off.

        """

        if value not in (True, False):
            raise TypeError(f'detect hidden windows must be a boolean, got object of type {type(value)}')
        args = []
        if value is True:
            args.append('On')
        else:
            args.append('Off')
        await self._transport.function_call('AHKSetDetectHiddenWindows', args=args)
        return None

    @staticmethod
    def _format_win_args(
        title: str,
        text: str,
        exclude_title: str,
        exclude_text: str,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
    ) -> List[str]:
        args = [title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        return args

    # fmt: off
    @overload
    async def list_windows(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> List[AsyncWindow]: ...
    @overload
    async def list_windows(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    @overload
    async def list_windows(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> List[AsyncWindow]: ...
    @overload
    async def list_windows(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    # fmt: on
    async def list_windows(
        self,
        *,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWindowList', args, engine=self, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def get_mouse_position(self, *, blocking: Literal[True]) -> Tuple[int, int]: ...
    @overload
    async def get_mouse_position(self, *, blocking: Literal[False]) -> AsyncFutureResult[Tuple[int, int]]: ...
    @overload
    async def get_mouse_position(self) -> Tuple[int, int]: ...
    @overload
    async def get_mouse_position(self, *, blocking: bool = True) -> Union[Tuple[int, int], AsyncFutureResult[Tuple[int, int]]]: ...
    # fmt: on
    async def get_mouse_position(
        self, *, blocking: bool = True
    ) -> Union[Tuple[int, int], AsyncFutureResult[Tuple[int, int]]]:
        resp = await self._transport.function_call('AHKMouseGetPos', blocking=blocking)
        return resp

    @property
    def mouse_position(self) -> AsyncPropertyReturnTupleIntInt:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('mouse_position'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_mouse_position()

    # fmt: off
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, speed: Optional[int] = None, relative: bool = False) -> None: ...
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, blocking: Literal[True], speed: Optional[int] = None, relative: bool = False) -> None: ...
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, blocking: Literal[False], speed: Optional[int] = None, relative: bool = False, ) -> AsyncFutureResult[None]: ...
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, speed: Optional[int] = None, relative: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        speed: Optional[int] = None,
        relative: bool = False,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        if relative and (x is None or y is None):
            x = x or 0
            y = y or 0
        elif not relative and (x is None or y is None):
            posx, posy = await self.get_mouse_position()
            x = x or posx
            y = y or posy

        if speed is None:
            speed = 2
        args = [str(x), str(y), str(speed)]
        if relative:
            args.append('R')
        resp = await self._transport.function_call('AHKMouseMove', args, blocking=blocking)
        return resp

    async def a_run_script(self, script_text: str, decode: bool = True, blocking: bool = True, **runkwargs: Any) -> str:
        raise NotImplementedError()

    # fmt: off
    @overload
    async def get_active_window(self) -> Optional[AsyncWindow]: ...
    @overload
    async def get_active_window(self, blocking: Literal[True]) -> Optional[AsyncWindow]: ...
    @overload
    async def get_active_window(self, blocking: Literal[False]) -> AsyncFutureResult[Optional[AsyncWindow]]: ...
    @overload
    async def get_active_window(self, blocking: bool = True) -> Union[Optional[AsyncWindow], AsyncFutureResult[Optional[AsyncWindow]]]: ...
    # fmt: on
    async def get_active_window(
        self, blocking: bool = True
    ) -> Union[Optional[AsyncWindow], AsyncFutureResult[Optional[AsyncWindow]]]:
        return await self.win_get(
            title='A', detect_hidden_windows=False, title_match_mode=(1, 'Fast'), blocking=blocking
        )

    @property
    def active_window(self) -> AsyncPropertyReturnOptionalAsyncWindow:
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('active_window'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_active_window()

    async def find_windows(
        self,
        func: Optional[AsyncFilterFunc] = None,
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        exact: Optional[bool] = None,
    ) -> List[AsyncWindow]:
        if exact is not None and title_match_mode is not None:
            raise TypeError('exact and match_mode parameters are mutually exclusive')
        if exact is not None:
            warnings.warn('exact parameter is deprecated. Use match_mode=3 instead', stacklevel=2)
            if exact:
                title_match_mode = (3, 'Fast')
            else:
                title_match_mode = (1, 'Fast')
        elif title_match_mode is None:
            title_match_mode = (1, 'Fast')

        windows = await self.list_windows(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
        )
        if func is None:
            return windows
        else:
            ret: List[AsyncWindow] = []
            for win in windows:
                match = await func(win)
                if match:
                    ret.append(win)
            return ret

    async def find_windows_by_class(
        self, class_name: str, *, exact: Optional[bool] = None, title_match_mode: Optional[TitleMatchMode] = None
    ) -> List[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ret = await self.find_windows(
                title=f'ahk_class {class_name}', title_match_mode=title_match_mode, exact=exact
            )
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return ret

    async def find_windows_by_text(
        self, text: str, exact: Optional[bool] = None, title_match_mode: Optional[TitleMatchMode] = None
    ) -> List[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ret = await self.find_windows(text=text, exact=exact, title_match_mode=title_match_mode)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return ret

    async def find_windows_by_title(
        self, title: str, exact: Optional[bool] = None, title_match_mode: Optional[TitleMatchMode] = None
    ) -> List[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            ret = await self.find_windows(title=title, exact=exact, title_match_mode=title_match_mode)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return ret

    async def find_window(
        self,
        func: Optional[AsyncFilterFunc] = None,
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        exact: Optional[bool] = None,
    ) -> Optional[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            windows = await self.find_windows(
                func,
                title=title,
                text=text,
                exclude_title=exclude_title,
                exclude_text=exclude_text,
                exact=exact,
                title_match_mode=title_match_mode,
            )
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return windows[0] if windows else None

    async def find_window_by_class(
        self, class_name: str, exact: Optional[bool] = None, title_match_mode: Optional[TitleMatchMode] = None
    ) -> Optional[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            windows = await self.find_windows_by_class(
                class_name=class_name, exact=exact, title_match_mode=title_match_mode
            )
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return windows[0] if windows else None

    async def find_window_by_text(
        self, text: str, exact: Optional[bool] = None, title_match_mode: Optional[TitleMatchMode] = None
    ) -> Optional[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            windows = await self.find_windows_by_text(text=text, exact=exact, title_match_mode=title_match_mode)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return windows[0] if windows else None

    async def find_window_by_title(
        self, title: str, exact: Optional[bool] = None, title_match_mode: Optional[TitleMatchMode] = None
    ) -> Optional[AsyncWindow]:
        with warnings.catch_warnings(record=True) as caught_warnings:
            windows = await self.find_windows_by_title(title=title, exact=exact, title_match_mode=title_match_mode)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return windows[0] if windows else None

    async def get_volume(self, device_number: int = 1) -> float:
        raise NotImplementedError()

    # fmt: off
    @overload
    async def key_down(self, key: Union[str, Key]) -> None: ...
    @overload
    async def key_down(self, key: Union[str, Key], *, blocking: Literal[True]) -> None: ...
    @overload
    async def key_down(self, key: Union[str, Key], *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def key_down(self, key: Union[str, Key], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def key_down(self, key: Union[str, Key], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        if isinstance(key, str):
            key = Key(key_name=key)
        if blocking:
            await self.send_input(key.DOWN, blocking=True)
            return None
        else:
            return await self.send_input(key.DOWN, blocking=False)

    # fmt: off
    @overload
    async def key_press(self, key: Union[str, Key], *, release: bool = True) -> None: ...
    @overload
    async def key_press(self, key: Union[str, Key], *, blocking: Literal[True], release: bool = True) -> None: ...
    @overload
    async def key_press(self, key: Union[str, Key], *, blocking: Literal[False], release: bool = True) -> AsyncFutureResult[None]: ...
    @overload
    async def key_press(self, key: Union[str, Key], *, release: bool = True, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def key_press(
        self, key: Union[str, Key], *, release: bool = True, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        if blocking:
            await self.key_down(key, blocking=True)
            if release:
                await self.key_up(key, blocking=True)
            return None
        else:
            d = await self.key_down(key, blocking=False)
            if release:
                return await self.key_up(key, blocking=False)
            return d

    # fmt: off
    @overload
    async def key_release(self, key: Union[str, Key]) -> None: ...
    @overload
    async def key_release(self, key: Union[str, Key], *, blocking: Literal[True]) -> None: ...
    @overload
    async def key_release(self, key: Union[str, Key], *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def key_release(self, key: Union[str, Key], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def key_release(self, key: Union[str, Key], *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        if blocking:
            await self.key_up(key=key, blocking=True)
            return None
        else:
            return await self.key_up(key=key, blocking=False)

    # fmt: off
    @overload
    async def key_state(self, key_name: str, *, mode: Optional[Literal['T', 'P']] = None) -> Union[float, int, str, None]: ...
    @overload
    async def key_state(self, key_name: str, *, mode: Optional[Literal['T', 'P']] = None, blocking: Literal[True]) -> Union[float, int, str, None]: ...
    @overload
    async def key_state(self, key_name: str, *, mode: Optional[Literal['T', 'P']] = None, blocking: Literal[False]) -> Union[AsyncFutureResult[str], AsyncFutureResult[int], AsyncFutureResult[float], AsyncFutureResult[None]]: ...
    @overload
    async def key_state(self, key_name: str, *, mode: Optional[Literal['T', 'P']] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None], Union[str, AsyncFutureResult[str]], Union[int, AsyncFutureResult[int]], Union[float, AsyncFutureResult[float]]]: ...
    # fmt: on
    async def key_state(
        self, key_name: str, *, mode: Optional[Literal['T', 'P']] = None, blocking: bool = True
    ) -> Union[
        int,
        float,
        str,
        None,
        AsyncFutureResult[str],
        AsyncFutureResult[int],
        AsyncFutureResult[float],
        AsyncFutureResult[None],
    ]:
        args: List[str] = [key_name]
        if mode is not None:
            if mode not in ('T', 'P'):
                raise ValueError(f'Invalid value for mode parameter. Mode must be `T` or `P`. Got {mode!r}')
            args.append(mode)
        return await self._transport.function_call('AHKKeyState', args, blocking=blocking)

    # fmt: off
    @overload
    async def key_up(self, key: Union[str, Key]) -> None: ...
    @overload
    async def key_up(self, key: Union[str, Key], *, blocking: Literal[True]) -> None: ...
    @overload
    async def key_up(self, key: Union[str, Key], *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def key_up(self, key: Union[str, Key], blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def key_up(self, key: Union[str, Key], blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        if isinstance(key, str):
            key = Key(key_name=key)
        if blocking:
            await self.send_input(key.UP, blocking=True)
            return None
        else:
            return await self.send_input(key.UP, blocking=False)

    # fmt: off
    @overload
    async def key_wait(self, key_name: str, *, timeout: Optional[int] = None, logical_state: bool = False, released: bool = False) -> int: ...
    @overload
    async def key_wait(self, key_name: str, *, blocking: Literal[True], timeout: Optional[int] = None, logical_state: bool = False, released: bool = False) -> int: ...
    @overload
    async def key_wait(self, key_name: str, *, blocking: Literal[False], timeout: Optional[int] = None, logical_state: bool = False, released: bool = False) -> AsyncFutureResult[int]: ...
    @overload
    async def key_wait(self, key_name: str, *, timeout: Optional[int] = None, logical_state: bool = False, released: bool = False, blocking: bool = True) -> Union[int, AsyncFutureResult[int]]: ...
    # fmt: on
    async def key_wait(
        self,
        key_name: str,
        *,
        timeout: Optional[int] = None,
        logical_state: bool = False,
        released: bool = False,
        blocking: bool = True,
    ) -> Union[int, AsyncFutureResult[int]]:
        options = ''
        if not released:
            options += 'D'
        if logical_state:
            options += 'L'
        if timeout:
            options += f'T{timeout}'
        args = [key_name]
        if options:
            args.append(options)

        resp = await self._transport.function_call('AHKKeyWait', args)
        return resp

    async def run_script(self, script_text: str, decode: bool = True, blocking: bool = True, **runkwargs: Any) -> str:
        raise NotImplementedError()

    async def set_send_level(self, level: int) -> None:
        if not isinstance(level, int):
            raise TypeError('level must be an integer between 0 and 100')
        if not 0 <= level <= 100:
            raise ValueError('level value must be between 0 and 100')
        args = [str(level)]
        await self._transport.function_call('AHKSetSendLevel', args)

    async def get_send_level(self) -> int:
        resp = await self._transport.function_call('AHKGetSendLevel')
        return resp

    # fmt: off
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None) -> None: ...
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send(
        self,
        s: str,
        *,
        raw: bool = False,
        key_delay: Optional[int] = None,
        key_press_duration: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [s]
        if key_delay:
            args.append(str(key_delay))
        else:
            args.append('')
        if key_press_duration:
            args.append(str(key_press_duration))
        else:
            args.append('')

        if raw:
            raw_resp = await self._transport.function_call('AHKSendRaw', args=args, blocking=blocking)
            return raw_resp
        else:
            resp = await self._transport.function_call('AHKSend', args=args, blocking=blocking)
            return resp

    # fmt: off
    @overload
    async def send_raw(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None) -> None: ...
    @overload
    async def send_raw(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def send_raw(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send_raw(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send_raw(
        self,
        s: str,
        *,
        key_delay: Optional[int] = None,
        key_press_duration: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        resp = await self.send(
            s, raw=True, key_delay=key_delay, key_press_duration=key_press_duration, blocking=blocking
        )
        return resp

    # fmt: off
    @overload
    async def send_input(self, s: str) -> None: ...
    @overload
    async def send_input(self, s: str, *, blocking: Literal[True]) -> None: ...
    @overload
    async def send_input(self, s: str, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send_input(self, s: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send_input(self, s: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        args = [s]
        resp = await self._transport.function_call('AHKSendInput', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def send_play(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None) -> None: ...
    @overload
    async def send_play(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def send_play(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send_play(self, s: str, *, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send_play(
        self,
        s: str,
        *,
        key_delay: Optional[int] = None,
        key_press_duration: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [s]
        if key_delay:
            args.append(str(key_delay))
        else:
            args.append('')
        if key_press_duration:
            args.append(str(key_press_duration))
        else:
            args.append('')

        resp = await self._transport.function_call('AHKSendPlay', args=args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def set_capslock_state(self, state: Optional[Literal[0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None) -> None: ...
    @overload
    async def set_capslock_state(self, state: Optional[Literal[0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_capslock_state(self, state: Optional[Literal[0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_capslock_state(self, state: Optional[Literal[0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_capslock_state(
        self, state: Optional[Literal[0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        args: List[str] = []
        if state is not None:
            if str(state).lower() not in ('1', '0', 'on', 'off', 'alwayson', 'alwaysoff'):
                raise ValueError(
                    f'Invalid value for state. Must be one of On, Off, AlwaysOn, AlwaysOff or None. Got {state!r}'
                )
            args.append(str(state))
        return await self._transport.function_call('AHKSetCapsLockState', args, blocking=blocking)

    async def set_volume(self, value: int, device_number: int = 1) -> None:
        raise NotImplementedError()

    async def show_error_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        silent: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    async def show_info_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        silent: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    async def show_tooltip(
        self,
        text: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        *,
        second: float = 1.0,
        id: Optional[str] = None,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    async def show_warning_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        slient: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    async def sound_beep(self, frequency: int = 523, duration: int = 150) -> None:
        raise NotImplementedError()

    async def sound_get(
        self, device_number: int = 1, component_type: str = 'MASTER', control_type: str = 'VOLUME'
    ) -> None:
        raise NotImplementedError()

    async def sound_play(self, filename: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    async def sound_set(
        self,
        value: Union[str, int, float],
        device_number: int = 1,
        component_type: str = 'MASTER',
        control_type: str = 'VOLUME',
    ) -> None:
        raise NotImplementedError()

    # fmt: off
    @overload
    async def win_get(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[AsyncWindow, None]]: ...
    @overload
    async def win_get(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[AsyncWindow, None, AsyncFutureResult[Union[None, AsyncWindow]]]: ...
    # fmt: on
    async def win_get(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[AsyncWindow, None, AsyncFutureResult[Union[None, AsyncWindow]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetID', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_get_text(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> str: ...
    @overload
    async def win_get_text(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def win_get_text(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> str: ...
    @overload
    async def win_get_text(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def win_get_text(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetText', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_title(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> str: ...
    @overload
    async def win_get_title(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def win_get_title(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> str: ...
    @overload
    async def win_get_title(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def win_get_title(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetTitle', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_class(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> str: ...
    @overload
    async def win_get_class(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def win_get_class(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> str: ...
    @overload
    async def win_get_class(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def win_get_class(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetClass', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_position(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[Position, None]: ...
    @overload
    async def win_get_position(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[Position, None]]: ...
    @overload
    async def win_get_position(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[Position, None]: ...
    @overload
    async def win_get_position(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[Position, None, AsyncFutureResult[Union[Position, None]]]: ...
    # fmt: on
    async def win_get_position(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[Position, None, AsyncFutureResult[Union[Position, None]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetPos', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_get_idlast(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get_idlast(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[AsyncWindow, None]]: ...
    @overload
    async def win_get_idlast(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get_idlast(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[AsyncWindow, None, AsyncFutureResult[Union[AsyncWindow, None]]]: ...
    # fmt: on
    async def win_get_idlast(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[AsyncWindow, None, AsyncFutureResult[Union[AsyncWindow, None]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetIDLast', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_get_pid(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[int, None]: ...
    @overload
    async def win_get_pid(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[int, None]]: ...
    @overload
    async def win_get_pid(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[int, None]: ...
    @overload
    async def win_get_pid(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[int, None, AsyncFutureResult[Union[int, None]]]: ...
    # fmt: on
    async def win_get_pid(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[int, None, AsyncFutureResult[Union[int, None]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetPID', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_process_name(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[str, None]: ...
    @overload
    async def win_get_process_name(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[str, None]]: ...
    @overload
    async def win_get_process_name(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[str, None]: ...
    @overload
    async def win_get_process_name(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, str, AsyncFutureResult[Optional[str]]]: ...
    # fmt: on
    async def win_get_process_name(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, str, AsyncFutureResult[Optional[str]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetProcessName', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_process_path(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[str, None]: ...
    @overload
    async def win_get_process_path(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[str, None]]: ...
    @overload
    async def win_get_process_path(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[str, None]: ...
    @overload
    async def win_get_process_path(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[str, None, Union[None, str, AsyncFutureResult[Optional[str]]]]: ...
    # fmt: on
    async def win_get_process_path(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[str, None, Union[None, str, AsyncFutureResult[Optional[str]]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetProcessPath', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_count(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> int: ...
    @overload
    async def win_get_count(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[int]: ...
    @overload
    async def win_get_count(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> int: ...
    @overload
    async def win_get_count(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[int, AsyncFutureResult[int]]: ...
    # fmt: on
    async def win_get_count(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[int, AsyncFutureResult[int]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetCount', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_minmax(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[int, None]: ...
    @overload
    async def win_get_minmax(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[int, None]]: ...
    @overload
    async def win_get_minmax(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[int, None]: ...
    @overload
    async def win_get_minmax(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, int, AsyncFutureResult[Optional[int]]]: ...
    # fmt: on
    async def win_get_minmax(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, int, AsyncFutureResult[Optional[int]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetMinMax', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_get_control_list(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[List[AsyncControl], None]: ...
    @overload
    async def win_get_control_list(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[List[AsyncControl], None]]: ...
    @overload
    async def win_get_control_list(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[List[AsyncControl], None]: ...
    @overload
    async def win_get_control_list(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[List[AsyncControl], None, AsyncFutureResult[Optional[List[AsyncControl]]]]: ...
    # fmt: on
    async def win_get_control_list(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[List[AsyncControl], None, AsyncFutureResult[Optional[List[AsyncControl]]]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinGetControlList', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_get_from_mouse_position(self) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get_from_mouse_position(self, *, blocking: Literal[False]) -> AsyncFutureResult[Union[AsyncWindow, None]]: ...
    @overload
    async def win_get_from_mouse_position(self, *, blocking: Literal[True]) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get_from_mouse_position(self, *, blocking: bool = True) -> Union[Optional[AsyncWindow], AsyncFutureResult[Optional[AsyncWindow]]]: ...
    # fmt: on
    async def win_get_from_mouse_position(
        self, *, blocking: bool = True
    ) -> Union[Optional[AsyncWindow], AsyncFutureResult[Optional[AsyncWindow]]]:
        resp = await self._transport.function_call('AHKWinFromMouse', blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_exists(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> bool: ...
    @overload
    async def win_exists(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...
    @overload
    async def win_exists(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> bool: ...
    @overload
    async def win_exists(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...
    # fmt: on
    async def win_exists(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[bool, AsyncFutureResult[bool]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinExist', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_activate(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_activate(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_activate(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_activate(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_activate(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinActivate', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_title(self, new_title: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_title(self, new_title: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_title(self, new_title: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_title(self, new_title: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_title(
        self,
        new_title: str,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [new_title, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetTitle', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_always_on_top(self, toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_always_on_top(
        self,
        toggle: Literal['On', 'Off', 'Toggle', 1, -1, 0],
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [str(toggle), title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetAlwaysOnTop', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_bottom(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_bottom(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_bottom(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_bottom(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_bottom(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinSetBottom', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_top(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_top(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_top(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_top(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_top(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinSetTop', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_disable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_disable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_disable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_disable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_disable(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinSetDisable', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_enable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_enable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_enable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_enable(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_enable(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinSetEnable', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_redraw(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_redraw(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_redraw(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_redraw(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_redraw(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinSetRedraw', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> bool: ...
    @overload
    async def win_set_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...
    @overload
    async def win_set_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> bool: ...
    @overload
    async def win_set_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...
    # fmt: on
    async def win_set_style(
        self,
        style: str,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[bool, AsyncFutureResult[bool]]:
        args = [style, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetStyle', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_ex_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> bool: ...
    @overload
    async def win_set_ex_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...
    @overload
    async def win_set_ex_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> bool: ...
    @overload
    async def win_set_ex_style(self, style: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...
    # fmt: on
    async def win_set_ex_style(
        self,
        style: str,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[bool, AsyncFutureResult[bool]]:
        args = [style, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetExStyle', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_region(self, options: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> bool: ...
    @overload
    async def win_set_region(self, options: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...
    @overload
    async def win_set_region(self, options: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> bool: ...
    @overload
    async def win_set_region(self, options: str, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...
    # fmt: on
    async def win_set_region(
        self,
        options: str,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[bool, AsyncFutureResult[bool]]:
        args = [options, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetRegion', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_transparent(self, transparency: Union[int, Literal['Off']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_transparent(self, transparency: Union[int, Literal['Off']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_transparent(self, transparency: Union[int, Literal['Off']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_transparent(self, transparency: Union[int, Literal['Off']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_transparent(
        self,
        transparency: Union[int, Literal['Off']],
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [str(transparency), title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetTransparent', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_set_trans_color(self, color: Union[int, str], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_set_trans_color(self, color: Union[int, str], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_set_trans_color(self, color: Union[int, str], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_set_trans_color(self, color: Union[int, str], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_set_trans_color(
        self,
        color: Union[int, str],
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = [str(color), title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')
        resp = await self._transport.function_call('AHKWinSetTransColor', args, blocking=blocking)
        return resp

    # alias for backwards compatibility
    windows = list_windows

    # fmt: off
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None) -> None: ...
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, blocking: Literal[True], coord_mode: Optional[CoordModeRelativeTo] = None) -> None: ...
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, blocking: Literal[False], coord_mode: Optional[CoordModeRelativeTo] = None) -> AsyncFutureResult[None]: ...
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, blocking: bool = True, coord_mode: Optional[CoordModeRelativeTo] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def right_click(
        self,
        x: Optional[Union[int, Tuple[int, int]]] = None,
        y: Optional[int] = None,
        *,
        click_count: Optional[int] = None,
        direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None,
        relative: Optional[bool] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        button = 'R'
        return await self.click(
            x,
            y,
            button=button,
            click_count=click_count,
            direction=direction,
            relative=relative,
            blocking=blocking,
            coord_mode=coord_mode,
        )

    # fmt: off
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None) -> None: ...
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, blocking: Literal[True], coord_mode: Optional[CoordModeRelativeTo] = None) -> None: ...
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, blocking: Literal[False], coord_mode: Optional[CoordModeRelativeTo] = None) -> AsyncFutureResult[None]: ...
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, *, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, relative: Optional[bool] = None, blocking: bool = True, coord_mode: Optional[CoordModeRelativeTo] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def click(
        self,
        x: Optional[Union[int, Tuple[int, int]]] = None,
        y: Optional[int] = None,
        *,
        button: Optional[Union[MouseButton, str]] = None,
        click_count: Optional[int] = None,
        direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None,
        relative: Optional[bool] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        if x or y:
            if y is None and isinstance(x, tuple) and len(x) == 2:
                #  allow position to be specified by a two-sequence tuple
                x, y = x
            assert x is not None and y is not None, 'If provided, position must be specified by x AND y'
        if button is None:
            button = 'L'
        button = resolve_button(button)

        if relative:
            r = 'Rel'
        else:
            r = ''
        if coord_mode is None:
            coord_mode = ''
        args = [str(x), str(y), button, str(click_count), direction or '', r, coord_mode]
        resp = await self._transport.function_call('AHKClick', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None) -> Optional[Tuple[int, int]]: ...
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[Optional[Tuple[int, int]]]: ...
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None, blocking: Literal[True]) -> Optional[Tuple[int, int]]: ...
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None, blocking: bool = True) -> Union[Tuple[int, int], None, AsyncFutureResult[Optional[Tuple[int, int]]]]: ...
    # fmt: on
    async def image_search(
        self,
        image_path: str,
        upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0),
        lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None,
        *,
        color_variation: Optional[int] = None,
        coord_mode: Optional[CoordModeRelativeTo] = None,
        scale_height: Optional[int] = None,
        scale_width: Optional[int] = None,
        transparent: Optional[str] = None,
        icon: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[Tuple[int, int], None, AsyncFutureResult[Optional[Tuple[int, int]]]]:
        """
        https://www.autohotkey.com/docs/commands/ImageSearch.htm
        """

        if scale_height and not scale_width:
            scale_width = -1
        elif scale_width and not scale_height:
            scale_height = -1

        options: List[Union[str, int]] = []
        if icon:
            options.append(f'Icon{icon}')
        if color_variation is not None:
            options.append(color_variation)
        if transparent is not None:
            options.append(f'Trans{transparent}')
        if scale_width:
            options.append(f'w{scale_width}')
            options.append(f'h{scale_height}')

        x1, y1 = upper_bound
        if lower_bound:
            x2, y2 = lower_bound
        else:
            x2, y2 = ('A_ScreenWidth', 'A_ScreenHeight')

        args = [str(x1), str(y1), str(x2), str(y2)]
        if options:
            opts = ' '.join(f'*{opt}' for opt in options)
            args.append(opts)
        else:
            args.append(image_path)
        resp = await self._transport.function_call('AHKImageSearch', args, blocking=blocking)
        return resp

    async def mouse_drag(
        self,
        x: int,
        y: int,
        *,
        from_position: Optional[Tuple[int, int]] = None,
        speed: Optional[int] = None,
        button: MouseButton = 1,
        relative: Optional[bool] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
    ) -> None:
        if from_position:
            x1, y1 = from_position
            args = [str(button), str(x1), str(y1), str(x), str(y)]
        else:
            args = [str(button), '', '', str(x), str(y)]

        if speed:
            args.append(str(speed))
        else:
            args.append('')

        if relative:
            args.append('R')
        else:
            args.append('')

        if coord_mode:
            args.append(coord_mode)

        await self._transport.function_call('AHKMouseClickDrag', args, blocking=blocking)

    # fmt: off
    @overload
    async def pixel_get_color(self, x: int, y: int, *, coord_mode: Optional[CoordModeRelativeTo] = None, alt: bool = False, slow: bool = False, rgb: bool = True) -> str: ...
    @overload
    async def pixel_get_color(self, x: int, y: int, *, coord_mode: Optional[CoordModeRelativeTo] = None, alt: bool = False, slow: bool = False, rgb: bool = True, blocking: Literal[True]) -> str: ...
    @overload
    async def pixel_get_color(self, x: int, y: int, *, coord_mode: Optional[CoordModeRelativeTo] = None, alt: bool = False, slow: bool = False, rgb: bool = True, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def pixel_get_color(self, x: int, y: int, *, coord_mode: Optional[CoordModeRelativeTo] = None, alt: bool = False, slow: bool = False, rgb: bool = True, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def pixel_get_color(
        self,
        x: int,
        y: int,
        *,
        coord_mode: Optional[CoordModeRelativeTo] = None,
        alt: bool = False,
        slow: bool = False,
        rgb: bool = True,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        args = [str(x), str(y), coord_mode or '']

        options = ' '.join(word for word, val in zip(('Alt', 'Slow', 'RGB'), (alt, slow, rgb)) if val)
        args.append(options)

        resp = await self._transport.function_call('AHKPixelGetColor', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True) -> Optional[Tuple[int, int]]: ...
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True, blocking: Literal[True]) -> Optional[Tuple[int, int]]: ...
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True, blocking: Literal[False]) -> AsyncFutureResult[Optional[Tuple[int, int]]]: ...
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True, blocking: bool = True) -> Union[Optional[Tuple[int, int]], AsyncFutureResult[Optional[Tuple[int, int]]]]: ...
    # fmt: on
    async def pixel_search(
        self,
        search_region_start: Tuple[int, int],
        search_region_end: Tuple[int, int],
        color: Union[str, int],
        variation: int = 0,
        *,
        coord_mode: Optional[CoordModeRelativeTo] = None,
        fast: bool = True,
        rgb: bool = True,
        blocking: bool = True,
    ) -> Union[Optional[Tuple[int, int]], AsyncFutureResult[Optional[Tuple[int, int]]]]:
        x1, y1 = search_region_start
        x2, y2 = search_region_end
        args = [str(x1), str(y1), str(x2), str(y2), str(color), str(variation)]
        mode = ' '.join(word for word, val in zip(('Fast', 'RGB'), (fast, rgb)) if val)
        args.append(mode)
        args.append(coord_mode or '')
        resp = await self._transport.function_call('AHKPixelSearch', args, blocking=blocking)
        return resp

    async def show_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        type_id: int = 1,
        slient: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    # fmt: off
    @overload
    async def win_close(self, title: str = '', *, text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_close(self, title: str = '', *, text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_close(self, title: str = '', *, text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_close(self, title: str = '', *, text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', blocking: bool = True, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_close(
        self,
        title: str = '',
        *,
        text: str = '',
        seconds_to_wait: Optional[int] = None,
        exclude_title: str = '',
        exclude_text: str = '',
        blocking: bool = True,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        args: List[str]
        args = [title, text, str(seconds_to_wait) if seconds_to_wait is not None else '', exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('On')
            elif detect_hidden_windows is False:
                args.append('Off')
            else:
                raise TypeError(
                    f'Invalid value for parameter detect_hidden_windows. Expected boolean or None, got {detect_hidden_windows!r}'
                )
        else:
            args.append('')
        if title_match_mode is not None:
            if isinstance(title_match_mode, tuple):
                match_mode, match_speed = title_match_mode
            elif title_match_mode in (1, 2, 3, 'RegEx'):
                match_mode = title_match_mode
                match_speed = ''
            elif title_match_mode in ('Fast', 'Slow'):
                match_mode = ''
                match_speed = title_match_mode
            else:
                raise ValueError(
                    f"Invalid value for title_match_mode argument. Expected 1, 2, 3, 'RegEx', 'Fast', 'Slow' or a tuple of these. Got {title_match_mode!r}"
                )
            args.append(str(match_mode))
            args.append(str(match_speed))
        else:
            args.append('')
            args.append('')

        resp = await self._transport.function_call('AHKWinClose', args=args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_kill(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_kill(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def win_kill(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_kill(self, *, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_kill(
        self,
        *,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinKill', args, engine=self, blocking=blocking)
        return resp

    async def block_forever(self) -> NoReturn:
        while True:
            await async_sleep(1)
