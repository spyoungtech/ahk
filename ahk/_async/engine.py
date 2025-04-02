from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
import warnings
from functools import partial
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Coroutine
from typing import Generic
from typing import List
from typing import Literal
from typing import NoReturn
from typing import Optional
from typing import overload
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from .transport import AsyncDaemonProcessTransport
from .transport import AsyncFutureResult
from .transport import AsyncTransport
from .window import AsyncControl
from .window import AsyncWindow
from ahk._hotkey import Hotkey
from ahk._hotkey import Hotstring
from ahk._types import _BUTTONS
from ahk._types import Coordinates
from ahk._types import CoordModeRelativeTo
from ahk._types import CoordModeTargets
from ahk._types import MouseButton
from ahk._types import Position
from ahk._types import SendMode
from ahk._types import TitleMatchMode
from ahk._utils import _get_executable_major_version
from ahk._utils import _resolve_executable_path
from ahk._utils import MsgBoxButtons
from ahk._utils import MsgBoxDefaultButton
from ahk._utils import MsgBoxIcon
from ahk._utils import MsgBoxModality
from ahk._utils import MsgBoxOtherOptions
from ahk._utils import type_escape
from ahk.directives import Directive
from ahk.extensions import _extension_registry
from ahk.extensions import _ExtensionMethodRegistry
from ahk.extensions import _resolve_extensions
from ahk.extensions import Extension
from ahk.keys import Key

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

async_sleep = asyncio.sleep  # unasync: remove
sleep = time.sleep

AsyncFilterFunc: TypeAlias = Callable[[AsyncWindow], Awaitable[bool]]  # unasync: remove
SyncFilterFunc: TypeAlias = Callable[[AsyncWindow], bool]

AsyncPropertyReturnTupleIntInt: TypeAlias = Coroutine[None, None, Coordinates]  # unasync: remove
SyncPropertyReturnTupleIntInt: TypeAlias = Coordinates

AsyncPropertyReturnOptionalAsyncWindow: TypeAlias = Coroutine[None, None, Optional[AsyncWindow]]  # unasync: remove
SyncPropertyReturnOptionalAsyncWindow: TypeAlias = Optional[AsyncWindow]

_PROPERTY_DEPRECATION_WARNING_MESSAGE = 'Use of the {0} property is not recommended (in the async API only) and may be removed in a future version. Use the get_{0} method instead'


def _resolve_button(button: Union[str, int]) -> str:
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
        resolved_button = f'X{button - 3}'
    else:
        assert isinstance(button, str)
        resolved_button = button
    return resolved_button


T_AHKVersion = TypeVar('T_AHKVersion', bound=Optional[Literal['v1', 'v2']])


class AsyncAHK(Generic[T_AHKVersion]):
    # fmt: off
    @overload
    def __init__(self: AsyncAHK[None], *, TransportClass: Optional[Type[AsyncTransport]] = None, directives: Optional[list[Directive | Type[Directive]]] = None, executable_path: str = '', extensions: list[Extension] | None | Literal['auto'] = None): ...
    @overload
    def __init__(self: AsyncAHK[None], *, TransportClass: Optional[Type[AsyncTransport]] = None, directives: Optional[list[Directive | Type[Directive]]] = None, executable_path: str = '', extensions: list[Extension] | None | Literal['auto'] = None, version: None): ...
    @overload
    def __init__(self: AsyncAHK[Literal['v2']], *, TransportClass: Optional[Type[AsyncTransport]] = None, directives: Optional[list[Directive | Type[Directive]]] = None, executable_path: str = '', extensions: list[Extension] | None | Literal['auto'] = None, version: Literal['v2']): ...
    @overload
    def __init__(self: AsyncAHK[Literal['v1']], *, TransportClass: Optional[Type[AsyncTransport]] = None, directives: Optional[list[Directive | Type[Directive]]] = None, executable_path: str = '', extensions: list[Extension] | None | Literal['auto'] = None, version: Literal['v1']): ...
    # fmt: on
    def __init__(
        self: AsyncAHK[Optional[Literal['v1', 'v2']]],
        *,
        TransportClass: Optional[Type[AsyncTransport]] = None,
        directives: Optional[list[Directive | Type[Directive]]] = None,
        executable_path: str = '',
        extensions: list[Extension] | None | Literal['auto'] = None,
        version: Optional[Literal['v1', 'v2']] = None,
    ):
        if version not in (None, 'v1', 'v2'):
            raise ValueError(f'Invalid version ({version!r}). Must be one of None, "v1", or "v2"')
        executable_path = _resolve_executable_path(executable_path=executable_path, version=version)
        skip_version_check = False
        if version is None:
            try:
                version = _get_executable_major_version(executable_path)
            except Exception as e:
                warnings.warn(
                    f'Could not detect AHK version ({e}). This is likely caused by a misconfigured AutoHotkey executable and will likely cause a fatal error later on.\nAssuming v1 for now.'
                )
                version = 'v1'
            skip_version_check = True

        if not skip_version_check:
            detected_version = _get_executable_major_version(executable_path)
            if version != detected_version:
                raise RuntimeError(
                    f'AutoHotkey {version} was requested but AutoHotkey {detected_version} was detected for executable {executable_path}'
                )
        self._version: Literal['v1', 'v2'] = version
        self._extension_registry: _ExtensionMethodRegistry
        self._extensions: list[Extension]
        if extensions == 'auto':
            self._extensions = [ext for ext in _extension_registry if ext._requires in (None, version)]
        else:
            self._extensions = _resolve_extensions(extensions) if extensions else []
            for ext in self._extensions:
                if ext._requires not in (None, version):
                    raise ValueError(
                        f'Incompatible extension detected. Extension requires AutoHotkey {ext._requires} but current version is {version}'
                    )
        self._method_registry = _ExtensionMethodRegistry(
            sync_methods={}, async_methods={}, async_window_methods={}, sync_window_methods={}
        )
        for ext in self._extensions:
            self._method_registry.merge(ext._extension_method_registry)
        if TransportClass is None:
            TransportClass = AsyncDaemonProcessTransport
        assert TransportClass is not None
        transport = TransportClass(
            executable_path=executable_path, directives=directives, extensions=self._extensions, version=version
        )
        self._transport: AsyncTransport = transport

    def __repr__(self) -> str:
        return f'<{self.__module__}.{self.__class__.__qualname__} object version={self._version!r}>'

    def __getattr__(self, name: str) -> Callable[..., Any]:
        is_async = False
        is_async = True  # unasync: remove
        if is_async:
            if name in self._method_registry.async_methods:
                method = self._method_registry.async_methods[name]
                return partial(method, self)
        else:
            if name in self._method_registry.sync_methods:
                method = self._method_registry.sync_methods[name]
                return partial(method, self)

        raise AttributeError(f'{self.__class__.__name__!r} object has no attribute {name!r}')

    def _get_window_extension_method(self, name: str) -> Callable[..., Any] | None:
        is_async = False
        is_async = True  # unasync: remove
        if is_async:
            if name in self._method_registry.async_window_methods:
                method = self._method_registry.async_window_methods[name]
                return method
        else:
            if name in self._method_registry.sync_window_methods:
                method = self._method_registry.sync_window_methods[name]
                return method
        return None

    def add_hotkey(
        self, keyname: str, callback: Callable[[], Any], ex_handler: Optional[Callable[[str, Exception], Any]] = None
    ) -> None:
        """
        Register a function to be called when a hotkey is pressed.

        Key notes:

        - You must call the `start_hotkeys` method for the hotkeys to be active
        - All hotkeys run in a single AHK process instance (but Python callbacks also get their own thread and can run simultaneously)
        - If you add a hotkey after the hotkey thread/instance is active, it will be restarted automatically
        - `async` functions are not directly supported as callbacks, however you may write a synchronous function that calls `asyncio.run`/`loop.create_task` etc.

        :param keyname: the key trigger for the hotkey, such as ``#n`` (win+n)
        :param callback: callback function to call when the hotkey is triggered
        :param ex_handler: a function which accepts two parameters: the keyname for the hotkey and the exception raised by the callback function.
        :return:
        """
        hotkey = Hotkey(keyname, callback, ex_handler=ex_handler)
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._transport.add_hotkey(hotkey=hotkey)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    async def function_call(self, function_name: str, args: list[str] | None = None, blocking: bool = True) -> Any:
        """
        Call an AHK function defined in the daemon script. This method is intended for use by extension authors.
        """
        if args is None:
            args = []
        return await self._transport.function_call(function_name, args, blocking=blocking, engine=self)  # type: ignore[call-overload]

    def add_hotstring(
        self,
        trigger: str,
        replacement_or_callback: Union[str, Callable[[], Any]],
        ex_handler: Optional[Callable[[str, Exception], Any]] = None,
        options: str = '',
    ) -> None:
        """
        Register a hotstring, e.g., `::btw::by the way`

        Key notes:

        - You must call the `start_hotkeys` method for registered hotstrings to be active
        - All hotstrings (and hotkeys) run in a single AHK process instance separate from other AHK processes.

        :param trigger: the trigger phrase for the hotstring, e.g., ``btw``
        :param replacement_or_callback: the replacement phrase (e.g., ``by the way``) or a Python callable to execute in response to the hotstring trigger
        :param ex_handler: a function which accepts two parameters: the hotstring and the exception raised by the callback function.
        :param options: the hotstring options -- same meanings as in AutoHotkey.
        :return:
        """
        hotstring = Hotstring(trigger, replacement_or_callback, ex_handler=ex_handler, options=options)
        with warnings.catch_warnings(record=True) as caught_warnings:
            self._transport.add_hotstring(hotstring=hotstring)
        if caught_warnings:
            for warning in caught_warnings:
                warnings.warn(warning.message, warning.category, stacklevel=2)
        return None

    def remove_hotkey(self, keyname: str) -> None:
        def _() -> None:
            return None

        h = Hotkey(keyname=keyname, callback=_)  # XXX: this can probably be avoided
        self._transport.remove_hotkey(hotkey=h)
        return None

    def clear_hotkeys(self) -> None:
        self._transport.clear_hotkeys()
        return None

    def remove_hotstring(self, trigger: str) -> None:
        hs = Hotstring(trigger=trigger, replacement_or_callback='')  # XXX: this can probably be avoided
        self._transport.remove_hotstring(hs)
        return None

    def clear_hotstrings(self) -> None:
        self._transport.clear_hotstrings()
        return None

    async def set_title_match_mode(self, title_match_mode: TitleMatchMode, /) -> None:
        """
        Sets the default title match mode

        Does not affect methods called with ``blocking=True`` (because these run in a separate AHK process)

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

        I.E. the current value of ``A_TitleMatchMode``

        """
        resp = await self._transport.function_call('AHKGetTitleMatchMode')
        return resp

    async def get_title_match_speed(self) -> str:
        """
        Get the title match mode speed.

        I.E. the current value of ``A_TitleMatchModeSpeed``

        """
        resp = await self._transport.function_call('AHKGetTitleMatchSpeed')
        return resp

    async def set_coord_mode(self, target: CoordModeTargets, relative_to: CoordModeRelativeTo = 'Screen') -> None:
        """
        Analog of `CoordMode <https://www.autohotkey.com/docs/commands/CoordMode.htm>`_
        """
        args = [str(target), str(relative_to)]
        await self._transport.function_call('AHKSetCoordMode', args)
        return None

    async def get_coord_mode(self, target: CoordModeTargets) -> str:
        """
        Analog for ``A_CoordMode<target>``
        """
        args = [str(target)]
        resp = await self._transport.function_call('AHKGetCoordMode', args)
        return resp

    async def set_send_mode(self, mode: SendMode) -> None:
        """
        Analog for `SendMode <https://www.autohotkey.com/docs/v1/lib/SendMode.htm>`_
        """
        args = [str(mode)]
        await self._transport.function_call('AHKSetSendMode', args)
        return None

    async def get_send_mode(self) -> str:
        resp = await self._transport.function_call('AHKGetSendMode')
        return resp

    # fmt: off
    @overload
    async def control_click(self, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def control_click(self, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def control_click(self, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def control_click(self, button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L', click_count: int = 1, options: str = '', control: str = '', title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def control_click(
        self,
        button: Literal['L', 'R', 'M', 'LEFT', 'RIGHT', 'MIDDLE'] = 'L',
        click_count: int = 1,
        options: str = '',
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
        Analog for `ControlClick <https://www.autohotkey.com/docs/commands/ControlClick.htm>`_
        """
        args = [control, title, text, str(button), str(click_count), options, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `ControlGetText <https://www.autohotkey.com/docs/commands/ControlGetText.htm>`_
        """
        args = [control, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog to `ControlGetPos <https://www.autohotkey.com/docs/commands/ControlGetPos.htm>`_
        """
        args = [control, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        Analog for `ControlSend <https://www.autohotkey.com/docs/commands/ControlSend.htm>`_
        """
        args = [control, keys, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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

    # TODO: raw option for control_send

    def start_hotkeys(self) -> None:
        """
        Start the Autohotkey process for triggering hotkeys

        """
        return self._transport.start_hotkeys()

    def stop_hotkeys(self) -> None:
        """
        Stop the Autohotkey process for triggering hotkeys/hotstrings

        """
        return self._transport.stop_hotkeys()

    async def set_detect_hidden_windows(self, value: bool) -> None:
        """
        Analog for `DetectHiddenWindows <https://www.autohotkey.com/docs/commands/DetectHiddenWindows.htm>`_

        :param value: The setting value. ``True`` to turn on hidden window detection, ``False`` to turn it off.
        """

        if value not in (True, False):
            raise TypeError(f'detect hidden windows must be a boolean, got object of type {type(value)}')
        args = []
        if value is True:
            args.append('1')
        else:
            args.append('0')
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
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
    async def list_windows(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> List[AsyncWindow]: ...
    @overload
    async def list_windows(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[List[AsyncWindow]]: ...
    @overload
    async def list_windows(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> List[AsyncWindow]: ...
    @overload
    async def list_windows(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]: ...
    # fmt: on
    async def list_windows(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[List[AsyncWindow], AsyncFutureResult[List[AsyncWindow]]]:
        """
        Enumerate all windows matching the criteria.

        Analog for `WinGet List subcommand <https://www.autohotkey.com/docs/v1/lib/WinGet.htm#List>_`
        """
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
    async def get_mouse_position(self, coord_mode: Optional[CoordModeRelativeTo] = None, *, blocking: Literal[True]) -> Coordinates: ...
    @overload
    async def get_mouse_position(self, coord_mode: Optional[CoordModeRelativeTo] = None, *, blocking: Literal[False]) -> AsyncFutureResult[Coordinates]: ...
    @overload
    async def get_mouse_position(self, coord_mode: Optional[CoordModeRelativeTo] = None) -> Coordinates: ...
    @overload
    async def get_mouse_position(self, coord_mode: Optional[CoordModeRelativeTo] = None, *, blocking: bool = True) -> Union[Coordinates, AsyncFutureResult[Coordinates]]: ...
    # fmt: on
    async def get_mouse_position(
        self, coord_mode: Optional[CoordModeRelativeTo] = None, *, blocking: bool = True
    ) -> Union[Coordinates, AsyncFutureResult[Coordinates]]:
        """
        Analog for `MouseGetPos <https://www.autohotkey.com/docs/commands/MouseGetPos.htm>`_
        """
        if coord_mode:
            args = [str(coord_mode)]
        else:
            args = []
        resp = await self._transport.function_call('AHKMouseGetPos', args, blocking=blocking)
        return resp

    @property
    def mouse_position(self) -> AsyncPropertyReturnTupleIntInt:
        """
        Convenience property for :py:meth:`get_mouse_position`

        Setter accepts a tuple of x,y coordinates passed to :py:meth:`mouse_mouse`
        """
        warnings.warn(  # unasync: remove
            _PROPERTY_DEPRECATION_WARNING_MESSAGE.format('mouse_position'), category=DeprecationWarning, stacklevel=2
        )
        return self.get_mouse_position()

    @mouse_position.setter
    def mouse_position(self, new_position: Tuple[int, int]) -> None:
        """
        Convenience setter for ``mouse_move``

        :param new_position: a tuple of x,y coordinates to move to
        """
        raise RuntimeError('Use of the mouse_position setter is not supported in the async API.')  # unasync: remove
        x, y = new_position
        return self.mouse_move(x=x, y=y, speed=0, relative=False)

    # fmt: off
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, speed: Optional[int] = None, relative: bool = False, send_mode: Optional[SendMode] = None, coord_mode: Optional[CoordModeRelativeTo] = None) -> None: ...
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, blocking: Literal[True], speed: Optional[int] = None, relative: bool = False, send_mode: Optional[SendMode] = None, coord_mode: Optional[CoordModeRelativeTo] = None) -> None: ...
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, blocking: Literal[False], speed: Optional[int] = None, relative: bool = False, send_mode: Optional[SendMode] = None, coord_mode: Optional[CoordModeRelativeTo] = None) -> AsyncFutureResult[None]: ...
    @overload
    async def mouse_move(self, x: Optional[Union[str, int]] = None, y: Optional[Union[str, int]] = None, *, speed: Optional[int] = None, relative: bool = False, blocking: bool = True, send_mode: Optional[SendMode] = None, coord_mode: Optional[CoordModeRelativeTo] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        speed: Optional[int] = None,
        relative: bool = False,
        send_mode: Optional[SendMode] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `MouseMove <https://www.autohotkey.com/docs/commands/MouseMove.htm>`_
        """
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
        else:
            args.append('')
        if send_mode:
            args.append(send_mode)
        else:
            args.append('')

        if coord_mode:
            args.append(coord_mode)
        else:
            args.append('')

        resp = await self._transport.function_call('AHKMouseMove', args, blocking=blocking)
        return resp

    async def a_run_script(self, *args: Any, **kwargs: Any) -> Union[str, AsyncFutureResult[str]]:
        """
        Deprecated. Use :py:meth:`run_script` instead.
        """
        warnings.warn('a_run_script is deprecated. Use run_script instead.', DeprecationWarning, stacklevel=2)
        return await self.run_script(*args, **kwargs)

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
        self: AsyncAHK[Any], blocking: bool = True
    ) -> Union[Optional[AsyncWindow], AsyncFutureResult[Optional[AsyncWindow]], AsyncFutureResult[AsyncWindow]]:
        """
        Gets the currently active window.
        """
        return await self.win_get(
            title='A', detect_hidden_windows=False, title_match_mode=(1, 'Fast'), blocking=blocking
        )

    # Ideally, this would be type-hinted for the AHK version. But we cant: https://github.com/python/mypy/issues/9937
    @property
    def active_window(self) -> AsyncPropertyReturnOptionalAsyncWindow:
        """
        Gets the currently active window. Convenience property for :py:meth:`get_active_window`
        """
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
            warnings.warn('exact parameter is deprecated. Use title_match_mode instead', stacklevel=2)
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
        """
        Analog for `SoundGetWaveVolume <https://www.autohotkey.com/docs/commands/SoundGetWaveVolume.htm>`_
        """
        args = [str(device_number)]
        response = await self._transport.function_call('AHKGetVolume', args)
        return response

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
        """
        Shortcut for :py:meth:`send_input` but transforms specified key to perform a key "DOWN" only (no release)
        """
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
        """
        Press (and release) a key. Sends `:py:meth:`key_down` then, if ``release`` is ``True`` (the default), sends
        :py:meth:`key_up` subsequently.
        """
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
        """
        Alias for :py:meth:`key_up`
        """
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
        """
        Analog for `GetKeyState <https://www.autohotkey.com/docs/commands/GetKeyState.htm#command>`_
        """
        args: List[str] = [key_name]
        if mode is not None:
            if mode not in ('T', 'P'):
                raise ValueError(f'Invalid value for mode parameter. Mode must be `T` or `P`. Got {mode!r}')
            args.append(mode)
        else:
            args.append('')
        resp = await self._transport.function_call('AHKKeyState', args, blocking=blocking)
        return resp

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
        """
        Shortcut for :py:meth:`send_input` but transforms specified key to perform a key "UP" only. Useful if the key
        was previously pressed down but not released.
        """
        if isinstance(key, str):
            key = Key(key_name=key)
        if blocking:
            await self.send_input(key.UP, blocking=True)
            return None
        else:
            return await self.send_input(key.UP, blocking=False)

    # fmt: off
    @overload
    async def key_wait(self, key_name: str, *, timeout: Optional[int | float] = None, logical_state: bool = False, released: bool = False) -> bool: ...
    @overload
    async def key_wait(self, key_name: str, *, blocking: Literal[True], timeout: Optional[int | float] = None, logical_state: bool = False, released: bool = False) -> bool: ...
    @overload
    async def key_wait(self, key_name: str, *, blocking: Literal[False], timeout: Optional[int | float] = None, logical_state: bool = False, released: bool = False) -> AsyncFutureResult[bool]: ...
    @overload
    async def key_wait(self, key_name: str, *, timeout: Optional[int | float] = None, logical_state: bool = False, released: bool = False, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...
    # fmt: on
    async def key_wait(
        self,
        key_name: str,
        *,
        timeout: Optional[int | float] = None,
        logical_state: bool = False,
        released: bool = False,
        blocking: bool = True,
    ) -> Union[bool, AsyncFutureResult[bool]]:
        """
        Analog for `KeyWait <https://www.autohotkey.com/docs/commands/KeyWait.htm>`_
        """
        options = ''
        if not released:
            options += 'D'
        if logical_state:
            options += 'L'
        if timeout is not None:
            assert timeout >= 0, 'Timeout value must be non-negative'
            options += f'T{timeout}'
        args = [key_name, options]

        resp = await self._transport.function_call('AHKKeyWait', args, blocking=blocking)
        return resp

    async def run_script(
        self, script_text_or_path: str, /, *, blocking: bool = True, timeout: Optional[int] = None
    ) -> Union[str, AsyncFutureResult[str]]:
        """
        Run an AutoHotkey script.
        Can either be a path to a script (``.ahk``) file or a string containing script contents
        """
        return await self._transport.run_script(script_text_or_path, blocking=blocking, timeout=timeout)

    async def set_send_level(self, level: int) -> None:
        """
        Analog for `SendLevel <https://www.autohotkey.com/docs/commands/SendLevel.htm>`_
        """
        if not isinstance(level, int):
            raise TypeError('level must be an integer between 0 and 100')
        if not 0 <= level <= 100:
            raise ValueError('level value must be between 0 and 100')
        args = [str(level)]
        await self._transport.function_call('AHKSetSendLevel', args)

    async def get_send_level(self) -> int:
        """
        Get the current `SendLevel <https://www.autohotkey.com/docs/commands/SendLevel.htm>`_
        (I.E. the value of ``A_SendLevel``)
        """
        resp = await self._transport.function_call('AHKGetSendLevel')
        return resp

    # fmt: off
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, send_mode: Optional[SendMode] = None) -> None: ...
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, send_mode: Optional[SendMode] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, send_mode: Optional[SendMode] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def send(self, s: str, *, raw: bool = False, key_delay: Optional[int] = None, key_press_duration: Optional[int] = None, send_mode: Optional[SendMode] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def send(
        self,
        s: str,
        *,
        raw: bool = False,
        key_delay: Optional[int] = None,
        key_press_duration: Optional[int] = None,
        send_mode: Optional[SendMode] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `Send <https://www.autohotkey.com/docs/v1/lib/Send.htm>`_
        """
        args = [s]
        if key_delay:
            args.append(str(key_delay))
        else:
            args.append('')
        if key_press_duration:
            args.append(str(key_press_duration))
        else:
            args.append('')
        if send_mode:
            args.append(send_mode)
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
        """
        Analog for `SendRaw <https://www.autohotkey.com/docs/v1/lib/Send.htm>`_
        """
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
        """
        Analog for `SendInput <https://www.autohotkey.com/docs/v1/lib/Send.htm>`_
        """
        args = [s, '', '']
        resp = await self._transport.function_call('AHKSendInput', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def type(self, s: str) -> None: ...
    @overload
    async def type(self, s: str, *, blocking: Literal[True]) -> None: ...
    @overload
    async def type(self, s: str, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def type(self, s: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def type(self, s: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        """
        Like :py:meth:`send_input` but performs necessary escapes for you.
        """
        resp = await self.send_input(type_escape(s), blocking=blocking)
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
        """
        Analog for `SendPlay <https://www.autohotkey.com/docs/v1/lib/Send.htm>`_
        """
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
    async def set_capslock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None) -> None: ...
    @overload
    async def set_capslock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_capslock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_capslock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_capslock_state(
        self,
        state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None,
        *,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `SetCapsLockState <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_
        """
        args: List[str] = []
        if state is not None:
            if str(state).lower() not in ('1', '0', 'on', 'off', 'alwayson', 'alwaysoff'):
                raise ValueError(
                    f'Invalid value for state. Must be one of On, Off, AlwaysOn, AlwaysOff or None. Got {state!r}'
                )
            if state is True:
                state = 'On'
            elif state is False:
                state = 'Off'

            args.append(str(state))
        else:
            args.append('')

        resp = await self._transport.function_call('AHKSetCapsLockState', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def set_numlock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None) -> None: ...
    @overload
    async def set_numlock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_numlock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_numlock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_numlock_state(
        self,
        state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None,
        *,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `SetCapsLockState <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_
        """
        args: List[str] = []
        if state is not None:
            if str(state).lower() not in ('1', '0', 'on', 'off', 'alwayson', 'alwaysoff'):
                raise ValueError(
                    f'Invalid value for state. Must be one of On, Off, AlwaysOn, AlwaysOff or None. Got {state!r}'
                )
            if state is True:
                state = 'On'
            elif state is False:
                state = 'Off'

            args.append(str(state))
        else:
            args.append('')

        resp = await self._transport.function_call('AHKSetNumLockState', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def set_scroll_lock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None) -> None: ...
    @overload
    async def set_scroll_lock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_scroll_lock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_scroll_lock_state(self, state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_scroll_lock_state(
        self,
        state: Optional[Literal[True, False, 0, 1, 'On', 'Off', 'AlwaysOn', 'AlwaysOff']] = None,
        *,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `SetCapsLockState <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_
        """
        args: List[str] = []
        if state is not None:
            if str(state).lower() not in ('1', '0', 'on', 'off', 'alwayson', 'alwaysoff'):
                raise ValueError(
                    f'Invalid value for state. Must be one of On, Off, AlwaysOn, AlwaysOff or None. Got {state!r}'
                )
            if state is True:
                state = 'On'
            elif state is False:
                state = 'Off'

            args.append(str(state))
        else:
            args.append('')

        resp = await self._transport.function_call('AHKSetScrollLockState', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def set_volume(self, value: int, device_number: int = 1) -> None: ...
    @overload
    async def set_volume(self, value: int, device_number: int = 1, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_volume(self, value: int, device_number: int = 1, *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_volume(self, value: int, device_number: int = 1, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_volume(
        self, value: int, device_number: int = 1, *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `SoundSetWaveVolume <https://www.autohotkey.com/docs/commands/SoundSetWaveVolume.htm>`_
        """
        args = [str(device_number), str(value)]
        return await self._transport.function_call('AHKSetVolume', args, blocking=blocking)

    # fmt: off

    # in v2 the "second" parameter is not supported
    @overload
    async def show_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, second: None = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, second: None = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, second: None = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, second: None = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    @overload
    async def show_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, type_id: int = 1, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def show_traytip(
        self,
        title: str,
        text: str,
        second: Optional[float] = None,
        type_id: int = 1,
        *,
        silent: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `TrayTip <https://www.autohotkey.com/docs/commands/TrayTip.htm>`_
        """
        if second is None:
            second = 1.0
        else:
            if self._version == 'v2':
                warnings.warn(
                    'supplying seconds is not supported when using AutoHotkey v2. This parameter will be ignored'
                )

        option = type_id + (16 if silent else 0) + (32 if large_icon else 0)
        args = [title, text, str(second), str(option)]
        return await self._transport.function_call('AHKTrayTip', args, blocking=blocking)

    # fmt: off
    @overload
    async def show_error_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_error_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_error_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_error_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    @overload
    async def show_error_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_error_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_error_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_error_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    # fmt: on
    async def show_error_traytip(
        self: AsyncAHK[Any],
        title: str,
        text: str,
        second: Optional[float] = None,
        *,
        silent: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Convenience method for :py:meth:`show_traytip` for error-style messages
        """
        return await self.show_traytip(
            title=title, text=text, second=second, type_id=3, silent=silent, large_icon=large_icon, blocking=blocking
        )

    # fmt: off
    @overload
    async def show_info_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_info_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_info_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_info_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    @overload
    async def show_info_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_info_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_info_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_info_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def show_info_traytip(
        self: AsyncAHK[Any],
        title: str,
        text: str,
        second: Optional[float] = None,
        *,
        silent: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Convenience method for :py:meth:`show_traytip` for info-style messages
        """
        return await self.show_traytip(
            title=title, text=text, second=second, type_id=1, silent=silent, large_icon=large_icon, blocking=blocking
        )

    # fmt: off
    @overload
    async def show_warning_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_warning_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_warning_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_warning_traytip(self: AsyncAHK[Literal['v2']], title: str, text: str, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...

    @overload
    async def show_warning_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False) -> None: ...
    @overload
    async def show_warning_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def show_warning_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: Literal[True]) -> None: ...
    @overload
    async def show_warning_traytip(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str, text: str, second: Optional[float] = None, *, silent: bool = False, large_icon: bool = False, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def show_warning_traytip(
        self: AsyncAHK[Any],
        title: str,
        text: str,
        second: Optional[float] = None,
        *,
        silent: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Convenience method for :py:meth:`show_traytip` for warning-style messages
        """
        return await self.show_traytip(
            title=title, text=text, second=second, type_id=2, silent=silent, large_icon=large_icon, blocking=blocking
        )

    async def show_tooltip(
        self,
        text: str = '',
        x: Optional[int] = None,
        y: Optional[int] = None,
        which: int = 1,
    ) -> None:
        """
        Analog for `ToolTip <https://www.autohotkey.com/docs/commands/ToolTip.htm>`_
        """
        if which not in range(1, 21):
            raise ValueError('which must be an integer between 1 and 20')
        args = [text]
        if x is not None:
            args.append(str(x))
        else:
            args.append('')
        if y is not None:
            args.append(str(y))
        else:
            args.append('')
        args.append(str(which))
        await self._transport.function_call('AHKShowToolTip', args)

    async def hide_tooltip(self, which: int = 1) -> None:
        await self.show_tooltip(which=which)

    async def menu_tray_tooltip(self, value: str) -> None:
        """
        Change the menu tray icon tooltip that appears when hovering the mouse over the tray icon.
        Does not affect tray icon for AHK processes started with :py:meth:`run_script` or ``blocking=False``

        Uses the `Tip subcommand <https://www.autohotkey.com/docs/v1/lib/Menu.htm#Tip>`_
        """

        args = [value]
        await self._transport.function_call('AHKMenuTrayTip', args)
        return None

    async def menu_tray_icon(self, filename: str = '*', icon_number: int = 1, freeze: Optional[bool] = None) -> None:
        """
        Change the tray icon menu.
        Does not affect tray icon for AHK processes started with :py:meth:`run_script` or ``blocking=False``

        Uses the `Icon subcommand <https://www.autohotkey.com/docs/v1/lib/Menu.htm#Icon>`_

        If called with no parameters, the tray icon will be reset to the original default.
        """
        args = [filename, str(icon_number)]
        if freeze is True:
            args.append('1')
        elif freeze is False:
            args.append('0')
        await self._transport.function_call('AHKMenuTrayIcon', args)
        return None

    async def menu_tray_icon_show(self) -> None:
        """
        Show ('unhide') the tray icon previously hidden by :py:class:`~ahk.directives.NoTrayIcon` directive.
        Does not affect tray icon for AHK processes started with :py:meth:`run_script` or ``blocking=False``
        """
        await self._transport.function_call('AHKMenuTrayShow')
        return None

    async def menu_tray_icon_hide(self) -> None:
        """
        hides the tray icon.
        Does not affect tray icon for AHK processes started with :py:meth:`run_script` or ``blocking=False``
        """
        await self._transport.function_call('AHKMenuTrayHide')
        return None

    # fmt: off
    @overload
    async def sound_beep(self, frequency: int = 523, duration: int = 150) -> None: ...
    @overload
    async def sound_beep(self, frequency: int = 523, duration: int = 150, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def sound_beep(self, frequency: int = 523, duration: int = 150, *, blocking: Literal[True]) -> None: ...
    @overload
    async def sound_beep(self, frequency: int = 523, duration: int = 150, *, blocking: bool = True) -> Optional[AsyncFutureResult[None]]: ...
    # fmt: on
    async def sound_beep(
        self, frequency: int = 523, duration: int = 150, *, blocking: bool = True
    ) -> Optional[AsyncFutureResult[None]]:
        """
        Analog for `SoundBeep <https://www.autohotkey.com/docs/commands/SoundBeep.htm>`_
        """
        args = [str(frequency), str(duration)]
        await self._transport.function_call('AHKSoundBeep', args, blocking=blocking)
        return None

    # fmt: off
    @overload
    async def sound_get(self, device_number: int = 1, component_type: str = 'MASTER', control_type: str = 'VOLUME') -> str: ...
    @overload
    async def sound_get(self, device_number: int = 1, component_type: str = 'MASTER', control_type: str = 'VOLUME', *, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def sound_get(self, device_number: int = 1, component_type: str = 'MASTER', control_type: str = 'VOLUME', *, blocking: Literal[True]) -> str: ...
    @overload
    async def sound_get(self, device_number: int = 1, component_type: str = 'MASTER', control_type: str = 'VOLUME', *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def sound_get(
        self,
        device_number: int = 1,
        component_type: str = 'MASTER',
        control_type: str = 'VOLUME',
        *,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        """
        Analog for `SoundGet <https://www.autohotkey.com/docs/commands/SoundGet.htm>`_
        """
        args = [str(device_number), component_type, control_type]
        return await self._transport.function_call('AHKSoundGet', args, blocking=blocking)

    # fmt: off
    @overload
    async def sound_play(self, filename: str) -> None: ...
    @overload
    async def sound_play(self, filename: str, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def sound_play(self, filename: str, *, blocking: Literal[True]) -> None: ...
    @overload
    async def sound_play(self, filename: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def sound_play(self, filename: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `SoundPlay <https://www.autohotkey.com/docs/commands/SoundPlay.htm>`_
        """
        return await self._transport.function_call('AHKSoundPlay', [filename], blocking=blocking)

    async def sound_set(
        self,
        value: Union[str, int, float],
        device_number: int = 1,
        component_type: str = 'MASTER',
        control_type: str = 'VOLUME',
        *,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `SoundSet <https://www.autohotkey.com/docs/commands/SoundSet.htm>`_
        """
        args = [str(device_number), component_type, control_type, str(value)]
        return await self._transport.function_call('AHKSoundSet', args, blocking=blocking)

    # fmt: off
    @overload
    async def win_get(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> AsyncWindow: ...
    @overload
    async def win_get(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[AsyncWindow]: ...
    @overload
    async def win_get(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> AsyncWindow: ...
    @overload
    async def win_get(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...

    @overload
    async def win_get(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[AsyncWindow, None]]: ...
    @overload
    async def win_get(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[AsyncWindow, None]: ...
    @overload
    async def win_get(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[AsyncWindow, None, AsyncFutureResult[Union[None, AsyncWindow]], AsyncFutureResult[AsyncWindow]]: ...
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
    ) -> Union[AsyncWindow, None, AsyncFutureResult[Union[None, AsyncWindow]], AsyncFutureResult[AsyncWindow]]:
        """
        Analog for `WinGet <https://www.autohotkey.com/docs/commands/WinGet.htm>`_
        """
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
        """
        Analog for `WinGetClass <https://www.autohotkey.com/docs/commands/WinGetClass.htm>`_
        """
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
    async def win_get_position(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Position: ...
    @overload
    async def win_get_position(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Position]: ...
    @overload
    async def win_get_position(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Position: ...
    @overload
    async def win_get_position(self: AsyncAHK[Literal['v2']], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[Position, AsyncFutureResult[Position]]: ...

    @overload
    async def win_get_position(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[Position, None]: ...
    @overload
    async def win_get_position(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[Union[Position, None]]: ...
    @overload
    async def win_get_position(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> Union[Position, None]: ...
    @overload
    async def win_get_position(self: Union[AsyncAHK[Literal['v1']], AsyncAHK[None]], title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[Position, None, AsyncFutureResult[Union[Position, None]]]: ...
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
    ) -> Union[Position, None, AsyncFutureResult[Union[Position, None]], AsyncFutureResult[Position]]:
        """
        Analog for `WinGetPos <https://www.autohotkey.com/docs/commands/WinGetPos.htm>`_
        """
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
        """
        Like the IDLast subcommand for WinGet
        """
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
        """
        Get a window by process ID.

        Like the pid subcommand for WinGet
        """
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
        """
        Get the process name of a window

        Analog for `ProcessName subcommand for WinGet <https://www.autohotkey.com/docs/v1/lib/WinGet.htm#ProcessName>`_
        """
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
        """
        Get the process path for a window.

        Analog for the `ProcessPath subcommand for WinGet <https://www.autohotkey.com/docs/v1/lib/WinGet.htm#ProcessPath>`_
        """
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
        """
        Analog for the `Count subcommand for WinGet <https://www.autohotkey.com/docs/v1/lib/WinGet.htm#Count>`_
        """
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
        """
        Analog for the `MinMax subcommand for WinGet <https://www.autohotkey.com/docs/v1/lib/WinGet.htm#MinMax>`_
        """
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
        """
        Analog for the `ControlList subcommand for WinGet <https://www.autohotkey.com/docs/v1/lib/WinGet.htm#ControlList>`_
        """
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
        """
        Analog for `WinActivate <https://www.autohotkey.com/docs/commands/WinActivate.htm>`_
        """
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
        """
        Analog for `WinSetTitle <https://www.autohotkey.com/docs/commands/WinSetTitle.htm>`_
        """
        args = [new_title, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `AlwaysOnTop subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#AlwaysOnTop>`_
        """
        args = [str(toggle), title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `Bottom subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Bottom>`_
        """
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
        """
        Analog for `Top subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Top>`_
        """
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
        """
        Analog for `Disable subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Disable>`_
        """
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
        """
        Analog for `Enable subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Enable>`_
        """
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
        """
        Analog for `Redraw subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Redraw>`_
        """

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
        """
        Analog for `Style subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Style>`_
        """

        args = [style, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `ExStyle subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#ExStyle>`_
        """
        args = [style, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `Region subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Region>`_
        """
        args = [options, title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `Transparent subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#Transparent>`_
        """
        args = [str(transparency), title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
        """
        Analog for `TransColor subcommand of WinSet <https://www.autohotkey.com/docs/v1/lib/WinSet.htm#TransColor>`_
        """
        args = [str(color), title, text, exclude_title, exclude_text]
        if detect_hidden_windows is not None:
            if detect_hidden_windows is True:
                args.append('1')
            elif detect_hidden_windows is False:
                args.append('0')
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
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> None: ...
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, blocking: Literal[True], coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> None: ...
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, blocking: Literal[False], coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> AsyncFutureResult[None]: ...
    @overload
    async def right_click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, blocking: bool = True, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def right_click(
        self,
        x: Optional[Union[int, Tuple[int, int]]] = None,
        y: Optional[int] = None,
        click_count: Optional[int] = None,
        direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None,
        *,
        relative: Optional[bool] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
        send_mode: Optional[SendMode] = None,
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
            send_mode=send_mode,
        )

    # fmt: off
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> None: ...
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, blocking: Literal[True], coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> None: ...
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, blocking: Literal[False], coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> AsyncFutureResult[None]: ...
    @overload
    async def click(self, x: Optional[Union[int, Tuple[int, int]]] = None, y: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, click_count: Optional[int] = None, direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None, *, relative: Optional[bool] = None, blocking: bool = True, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def click(
        self,
        x: Optional[Union[int, Tuple[int, int]]] = None,
        y: Optional[int] = None,
        button: Optional[Union[MouseButton, str]] = None,
        click_count: Optional[int] = None,
        direction: Optional[Literal['U', 'D', 'Up', 'Down']] = None,
        *,
        relative: Optional[bool] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
        send_mode: Optional[SendMode] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `Click <https://www.autohotkey.com/docs/commands/Click.htm>`_
        """
        if x or y:
            if y is None and isinstance(x, tuple) and len(x) == 2:
                #  allow position to be specified by a two-sequence tuple
                x, y = x
            assert x is not None and y is not None, 'If provided, position must be specified by x AND y'
        if button is None:
            button = 'L'
        button = _resolve_button(button)

        if relative:
            r = 'Rel'
        else:
            r = ''
        if coord_mode is None:
            coord_mode = ''
        if send_mode is None:
            send_mode = ''
        args = [str(x), str(y), button, str(click_count), direction or '', r, coord_mode, str(send_mode)]
        resp = await self._transport.function_call('AHKClick', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None) -> Optional[Coordinates]: ...
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[Optional[Coordinates]]: ...
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None, blocking: Literal[True]) -> Optional[Coordinates]: ...
    @overload
    async def image_search(self, image_path: str, upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0), lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None, *, color_variation: Optional[int] = None, coord_mode: Optional[CoordModeRelativeTo] = None, scale_height: Optional[int] = None, scale_width: Optional[int] = None, transparent: Optional[str] = None, icon: Optional[int] = None, blocking: bool = True) -> Union[Coordinates, None, AsyncFutureResult[Optional[Coordinates]]]: ...
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
    ) -> Union[Coordinates, None, AsyncFutureResult[Optional[Coordinates]]]:
        """
        Analog for `ImageSearch <https://www.autohotkey.com/docs/commands/ImageSearch.htm>`_
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
            args.append(opts + f' {image_path}')
        else:
            args.append(image_path)

        if coord_mode is not None:
            args.append(coord_mode)
        else:
            args.append('')

        resp = await self._transport.function_call('AHKImageSearch', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def mouse_drag(self, x: int, y: int, *, from_position: Optional[Tuple[int, int]] = None, speed: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> None: ...
    @overload
    async def mouse_drag(self, x: int, y: int, *, from_position: Optional[Tuple[int, int]] = None, speed: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def mouse_drag(self, x: int, y: int, *, from_position: Optional[Tuple[int, int]] = None, speed: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, relative: Optional[bool] = None, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def mouse_drag(self, x: int, y: int, *, from_position: Optional[Tuple[int, int]] = None, speed: Optional[int] = None, button: Optional[Union[MouseButton, str]] = None, relative: Optional[bool] = None, blocking: bool = True, coord_mode: Optional[CoordModeRelativeTo] = None, send_mode: Optional[SendMode] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def mouse_drag(
        self,
        x: int,
        y: int,
        *,
        from_position: Optional[Tuple[int, int]] = None,
        speed: Optional[int] = None,
        button: Optional[Union[MouseButton, str]] = None,
        relative: Optional[bool] = None,
        blocking: bool = True,
        coord_mode: Optional[CoordModeRelativeTo] = None,
        send_mode: Optional[SendMode] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `MouseClickDrag <https://www.autohotkey.com/docs/commands/MouseClickDrag.htm>`_
        """
        if button is None:
            button = 'Left'
        else:
            button = _resolve_button(button)
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
        else:
            args.append('')

        if send_mode:
            args.append(send_mode)
        else:
            args.append('')

        resp = await self._transport.function_call('AHKMouseClickDrag', args, blocking=blocking)
        return resp

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
        """
        Analog for `PixelGetColor <https://www.autohotkey.com/docs/commands/PixelGetColor.htm>`_
        """
        args = [str(x), str(y), coord_mode or '']

        options = ' '.join(word for word, val in zip(('Alt', 'Slow', 'RGB'), (alt, slow, rgb)) if val)
        args.append(options)

        resp = await self._transport.function_call('AHKPixelGetColor', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True) -> Optional[Coordinates]: ...
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True, blocking: Literal[True]) -> Optional[Coordinates]: ...
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True, blocking: Literal[False]) -> AsyncFutureResult[Optional[Coordinates]]: ...
    @overload
    async def pixel_search(self, search_region_start: Tuple[int, int], search_region_end: Tuple[int, int], color: Union[str, int], variation: int = 0, *, coord_mode: Optional[CoordModeRelativeTo] = None, fast: bool = True, rgb: bool = True, blocking: bool = True) -> Union[Optional[Coordinates], AsyncFutureResult[Optional[Coordinates]]]: ...
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
    ) -> Union[Optional[Coordinates], AsyncFutureResult[Optional[Coordinates]]]:
        """
        Analog for `PixelSearch <https://www.autohotkey.com/docs/commands/PixelSearch.htm>`_
        """
        x1, y1 = search_region_start
        x2, y2 = search_region_end
        args = [str(x1), str(y1), str(x2), str(y2), str(color), str(variation)]
        mode = ' '.join(word for word, val in zip(('Fast', 'RGB'), (fast, rgb)) if val)
        args.append(mode)
        args.append(coord_mode or '')
        resp = await self._transport.function_call('AHKPixelSearch', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_close(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_close(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_close(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_close(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, blocking: bool = True, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_close(
        self,
        title: str = '',
        text: str = '',
        seconds_to_wait: Optional[int] = None,
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        blocking: bool = True,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `WinClose <https://www.autohotkey.com/docs/commands/WinClose.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(seconds_to_wait) if seconds_to_wait else '')

        resp = await self._transport.function_call('AHKWinClose', args, engine=self, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_kill(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_kill(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def win_kill(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_kill(self, title: str = '', text: str = '', seconds_to_wait: Optional[int] = None, exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_kill(
        self,
        title: str = '',
        text: str = '',
        seconds_to_wait: Optional[int] = None,
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `WinKill <https://www.autohotkey.com/docs/commands/WinKill.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(seconds_to_wait) if seconds_to_wait else '')

        resp = await self._transport.function_call('AHKWinKill', args, engine=self, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_minimize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_minimize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def win_minimize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_minimize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_minimize(
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
        """
        Analog for `WinMinimize <https://www.autohotkey.com/docs/commands/WinMinimize.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinMinimize', args, engine=self, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_maximize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_maximize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def win_maximize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_maximize(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_maximize(
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
        """
        Analog for `WinMaximize <https://www.autohotkey.com/docs/commands/WinMaximize.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinMaximize', args, engine=self, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_restore(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_restore(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def win_restore(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_restore(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True,) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_restore(
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
        """
        Analog for `WinRestore <https://www.autohotkey.com/docs/commands/WinRestore.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinRestore', args, engine=self, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_wait(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None) -> AsyncWindow: ...
    @overload
    async def win_wait(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[AsyncWindow]: ...
    @overload
    async def win_wait(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[True]) -> AsyncWindow: ...
    @overload
    async def win_wait(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: bool = True) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...
    # fmt: on
    async def win_wait(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        timeout: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]:
        """
        Analog for `WinWait <https://www.autohotkey.com/docs/commands/WinWait.htm>`_
        """
        if not title and not text and not exclude_title and not exclude_text:
            raise ValueError(
                'Expected non-blank value for at least one of the following: title, text, exclude_title, exclude_text'
            )
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(timeout) if timeout else '')
        resp = await self._transport.function_call('AHKWinWait', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_wait_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None) -> AsyncWindow: ...
    @overload
    async def win_wait_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[AsyncWindow]: ...
    @overload
    async def win_wait_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[True]) -> AsyncWindow: ...
    @overload
    async def win_wait_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: bool = True) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...
    # fmt: on
    async def win_wait_active(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        timeout: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]:
        """
        Analog for `WinWaitActive <https://www.autohotkey.com/docs/commands/WinWaitActive.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(timeout) if timeout else '')
        resp = await self._transport.function_call('AHKWinWaitActive', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_wait_not_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None) -> AsyncWindow: ...
    @overload
    async def win_wait_not_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[AsyncWindow]: ...
    @overload
    async def win_wait_not_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[True]) -> AsyncWindow: ...
    @overload
    async def win_wait_not_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: bool = True) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]: ...
    # fmt: on
    async def win_wait_not_active(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        timeout: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[AsyncWindow, AsyncFutureResult[AsyncWindow]]:
        """
        Analog for `WinWaitNotActive <https://www.autohotkey.com/docs/commands/WinWaitActive.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(timeout) if timeout else '')
        resp = await self._transport.function_call('AHKWinWaitNotActive', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_wait_close(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None) -> None: ...
    @overload
    async def win_wait_close(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_wait_close(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_wait_close(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, timeout: Optional[int] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_wait_close(
        self,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        *,
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        timeout: Optional[int] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `WinWaitClose <https://www.autohotkey.com/docs/commands/WinWaitClose.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(timeout) if timeout else '')
        resp = await self._transport.function_call('AHKWinWaitClose', args, blocking=blocking, engine=self)
        return resp

    # fmt: off
    @overload
    async def win_show(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_show(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_show(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_show(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_show(
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
        """
        Analog for `WinShow <https://www.autohotkey.com/docs/commands/WinShow.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinShow', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_hide(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_hide(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_hide(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_hide(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_hide(
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
        """
        Analog for `WinHide <https://www.autohotkey.com/docs/commands/WinHide.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinHide', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_is_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> bool: ...
    @overload
    async def win_is_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> bool: ...
    @overload
    async def win_is_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[bool]: ...
    @overload
    async def win_is_active(self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', *, title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[bool, AsyncFutureResult[bool]]: ...
    # fmt: on
    async def win_is_active(
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
        """
        Check if a window is active.

        Uses `WinActive <https://www.autohotkey.com/docs/v1/lib/WinActive.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        resp = await self._transport.function_call('AHKWinIsActive', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def win_move(self, x: int, y: int, *, width: Optional[int] = None, height: Optional[int] = None, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None) -> None: ...
    @overload
    async def win_move(self, x: int, y: int, *, width: Optional[int] = None, height: Optional[int] = None, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[True]) -> None: ...
    @overload
    async def win_move(self, x: int, y: int, *, width: Optional[int] = None, height: Optional[int] = None, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def win_move(self, x: int, y: int, *, width: Optional[int] = None, height: Optional[int] = None, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '', title_match_mode: Optional[TitleMatchMode] = None, detect_hidden_windows: Optional[bool] = None, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def win_move(
        self,
        x: int,
        y: int,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
        title_match_mode: Optional[TitleMatchMode] = None,
        detect_hidden_windows: Optional[bool] = None,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `WinMove <https://www.autohotkey.com/docs/commands/WinMove.htm>`_
        """
        args = self._format_win_args(
            title=title,
            text=text,
            exclude_title=exclude_title,
            exclude_text=exclude_text,
            title_match_mode=title_match_mode,
            detect_hidden_windows=detect_hidden_windows,
        )
        args.append(str(x))
        args.append(str(y))
        args.append(str(width) if width is not None else '')
        args.append(str(height) if height is not None else '')
        resp = await self._transport.function_call('AHKWinMove', args, blocking=blocking)
        return resp

    # fmt: off
    @overload
    async def get_clipboard(self) -> str: ...
    @overload
    async def get_clipboard(self, *, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def get_clipboard(self, *, blocking: Literal[True]) -> str: ...
    @overload
    async def get_clipboard(self, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def get_clipboard(self, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]:
        """
        Get the string contents of the clipboard
        """
        return await self._transport.function_call('AHKGetClipboard', blocking=blocking)

    async def set_clipboard(self, s: str, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]:
        """
        Set the contents of the clipboard
        """
        args = [s]
        return await self._transport.function_call('AHKSetClipboard', args, blocking=blocking)

    async def get_clipboard_all(self, *, blocking: bool = True) -> Union[bytes, AsyncFutureResult[bytes]]:
        """
        Get the full binary contents of the keyboard. The return value is intended to be used with :py:meth:`set_clipboard_all`
        """
        return await self._transport.function_call('AHKGetClipboardAll', blocking=blocking)

    # fmt: off
    @overload
    async def set_clipboard_all(self, contents: bytes) -> None: ...
    @overload
    async def set_clipboard_all(self, contents: bytes, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def set_clipboard_all(self, contents: bytes, *, blocking: Literal[True]) -> None: ...
    @overload
    async def set_clipboard_all(self, contents: bytes, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def set_clipboard_all(
        self, contents: bytes, *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Set the full binary contents of the clipboard. Expects bytes object as returned by :py:meth:`get_clipboard_all`
        """
        # TODO: figure out how to do this without a tempfile
        if not isinstance(contents, bytes):
            raise ValueError('Malformed data. Can only set bytes as returned by get_clipboard_all')
        if not contents:
            raise ValueError('bytes must be nonempty. If you want to clear the clipboard, use `set_clipboard`')
        with tempfile.NamedTemporaryFile(prefix='ahk-python', suffix='.clip', mode='wb', delete=False) as f:
            f.write(contents)

        args = [f'*c {f.name}' if self._transport._version != 'v2' else f.name]
        try:
            resp = await self._transport.function_call('AHKSetClipboardAll', args, blocking=blocking)
            return resp
        finally:
            try:
                os.remove(f.name)
            except Exception:
                pass

    def on_clipboard_change(
        self, callback: Callable[[int], Any], ex_handler: Optional[Callable[[int, Exception], Any]] = None
    ) -> None:
        """
        call a function in response to clipboard change.
        Uses `OnClipboardChange() <https://www.autohotkey.com/docs/commands/OnClipboardChange.htm#function>`_
        """
        self._transport.on_clipboard_change(callback, ex_handler)

    # fmt: off
    @overload
    async def clip_wait(self, timeout: Optional[float] = None, wait_for_any_data: bool = False) -> None: ...
    @overload
    async def clip_wait(self, timeout: Optional[float] = None, wait_for_any_data: bool = False, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def clip_wait(self, timeout: Optional[float] = None, wait_for_any_data: bool = False, *, blocking: Literal[True]) -> None: ...
    @overload
    async def clip_wait(self, timeout: Optional[float] = None, wait_for_any_data: bool = False, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def clip_wait(
        self, timeout: Optional[float] = None, wait_for_any_data: bool = False, *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Wait until the clipboard contents change

        Analog for `ClipWait <https://www.autohotkey.com/docs/v1/lib/ClipWait.htm>`_
        """
        args = [str(timeout) if timeout else '']
        if wait_for_any_data:
            args.append('1')
        else:
            args.append('0')
        return await self._transport.function_call('AHKClipWait', args, blocking=blocking)

    async def block_input(
        self,
        value: Literal['On', 'Off', 'Default', 'Send', 'Mouse', 'MouseMove', 'MouseMoveOff', 'SendAndMouse'],
        /,  # flake8: noqa
    ) -> None:
        """
        Analog for `BlockInput <https://www.autohotkey.com/docs/commands/BlockInput.htm>`_
        """
        await self._transport.function_call('AHKBlockInput', args=[value])

    # fmt: off
    @overload
    async def reg_delete(self, key_name: str, value_name: Optional[str] = None) -> None: ...
    @overload
    async def reg_delete(self, key_name: str, value_name: Optional[str] = None, *, blocking: Literal[False]) -> Union[None, AsyncFutureResult[None]]: ...
    @overload
    async def reg_delete(self, key_name: str, value_name: Optional[str] = None, *, blocking: Literal[True]) -> None: ...
    @overload
    async def reg_delete(self, key_name: str, value_name: Optional[str] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def reg_delete(
        self, key_name: str, value_name: Optional[str] = None, *, blocking: bool = True
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `RegDelete <https://www.autohotkey.com/docs/commands/RegDelete.htm>`_
        """
        args = [key_name, value_name if value_name is not None else '']
        return await self._transport.function_call('AHKRegDelete', args, blocking=blocking)

    # fmt: off
    @overload
    async def reg_write(self, value_type: Literal['REG_SZ', 'REG_EXPAND_SZ', 'REG_MULTI_SZ', 'REG_DWORD', 'REG_BINARY'], key_name: str, value_name: Optional[str] = None, value: Optional[str] = None) -> None: ...
    @overload
    async def reg_write(self, value_type: Literal['REG_SZ', 'REG_EXPAND_SZ', 'REG_MULTI_SZ', 'REG_DWORD', 'REG_BINARY'], key_name: str, value_name: Optional[str] = None, value: Optional[str] = None, *, blocking: Literal[False]) -> AsyncFutureResult[None]: ...
    @overload
    async def reg_write(self, value_type: Literal['REG_SZ', 'REG_EXPAND_SZ', 'REG_MULTI_SZ', 'REG_DWORD', 'REG_BINARY'], key_name: str, value_name: Optional[str] = None, value: Optional[str] = None, *, blocking: Literal[True]) -> None: ...
    @overload
    async def reg_write(self, value_type: Literal['REG_SZ', 'REG_EXPAND_SZ', 'REG_MULTI_SZ', 'REG_DWORD', 'REG_BINARY'], key_name: str, value_name: Optional[str] = None, value: Optional[str] = None, *, blocking: bool = True) -> Union[None, AsyncFutureResult[None]]: ...
    # fmt: on
    async def reg_write(
        self,
        value_type: Literal['REG_SZ', 'REG_EXPAND_SZ', 'REG_MULTI_SZ', 'REG_DWORD', 'REG_BINARY'],
        key_name: str,
        value_name: Optional[str] = None,
        value: Optional[str] = None,
        *,
        blocking: bool = True,
    ) -> Union[None, AsyncFutureResult[None]]:
        """
        Analog for `RegWrite <https://www.autohotkey.com/docs/commands/RegWrite.htm>`_
        """
        args = [value_type, key_name]
        if value_name is not None:
            args.append(value_name)
        else:
            args.append('')
        if value is not None:
            args.append(value)
        else:
            args.append('')
        return await self._transport.function_call('AHKRegWrite', args, blocking=blocking)

    # fmt: off
    @overload
    async def reg_read(self, key_name: str, value_name: Optional[str] = None) -> str: ...
    @overload
    async def reg_read(self, key_name: str, value_name: Optional[str] = None, *, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def reg_read(self, key_name: str, value_name: Optional[str] = None, *, blocking: Literal[True]) -> str: ...
    @overload
    async def reg_read(self, key_name: str, value_name: Optional[str] = None, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def reg_read(
        self, key_name: str, value_name: Optional[str] = None, *, blocking: bool = True
    ) -> Union[str, AsyncFutureResult[str]]:
        """
        Analog for `RegRead <https://www.autohotkey.com/docs/commands/RegRead.htm>`_
        """
        args = [key_name]
        if value_name is not None:
            args.append(value_name)
        else:
            args.append('')
        return await self._transport.function_call('AHKRegRead', args, blocking=blocking)

    # fmt: off
    @overload
    async def msg_box(self, text: str = '', title: str = 'Message', buttons: MsgBoxButtons = MsgBoxButtons.OK, icon: Optional[MsgBoxIcon] = None, default_button: Optional[MsgBoxDefaultButton] = None, modality: Optional[MsgBoxModality] = None, help_button: bool = False, text_right_justified: bool = False, right_to_left_reading: bool = False, timeout: Optional[int] = None) -> str: ...
    @overload
    async def msg_box(self, text: str = '', title: str = 'Message', buttons: MsgBoxButtons = MsgBoxButtons.OK, icon: Optional[MsgBoxIcon] = None, default_button: Optional[MsgBoxDefaultButton] = None, modality: Optional[MsgBoxModality] = None, help_button: bool = False, text_right_justified: bool = False, right_to_left_reading: bool = False, timeout: Optional[int] = None, *, blocking: Literal[False]) -> AsyncFutureResult[str]: ...
    @overload
    async def msg_box(self, text: str = '', title: str = 'Message', buttons: MsgBoxButtons = MsgBoxButtons.OK, icon: Optional[MsgBoxIcon] = None, default_button: Optional[MsgBoxDefaultButton] = None, modality: Optional[MsgBoxModality] = None, help_button: bool = False, text_right_justified: bool = False, right_to_left_reading: bool = False, timeout: Optional[int] = None, *, blocking: Literal[True]) -> str: ...
    @overload
    async def msg_box(self, text: str = '', title: str = 'Message', buttons: MsgBoxButtons = MsgBoxButtons.OK, icon: Optional[MsgBoxIcon] = None, default_button: Optional[MsgBoxDefaultButton] = None, modality: Optional[MsgBoxModality] = None, help_button: bool = False, text_right_justified: bool = False, right_to_left_reading: bool = False, timeout: Optional[int] = None, *, blocking: bool = True) -> Union[str, AsyncFutureResult[str]]: ...
    # fmt: on
    async def msg_box(
        self,
        text: str = '',
        title: str = 'Message',
        buttons: MsgBoxButtons = MsgBoxButtons.OK,
        icon: Optional[MsgBoxIcon] = None,
        default_button: Optional[MsgBoxDefaultButton] = None,
        modality: Optional[MsgBoxModality] = None,
        help_button: bool = False,
        text_right_justified: bool = False,
        right_to_left_reading: bool = False,
        timeout: Optional[int] = None,
        *,
        blocking: bool = True,
    ) -> Union[str, AsyncFutureResult[str]]:
        options: int = int(buttons)
        for opt in (icon, default_button, modality):
            if opt is not None:
                options += opt
        if help_button:
            options += MsgBoxOtherOptions.HELP_BUTTON
        if text_right_justified:
            options += MsgBoxOtherOptions.TEXT_RIGHT_JUSTIFIED
        if right_to_left_reading:
            options += MsgBoxOtherOptions.RIGHT_TO_LEFT_READING_ORDER

        args = [str(options), title, text]
        if timeout is not None:
            args.append(str(timeout))
        else:
            args.append('')

        return await self._transport.function_call('AHKMsgBox', args, blocking=blocking)

    # fmt: off
    @overload
    async def input_box(self, prompt: str = '', title: str = 'Input', default: str = '', hide: bool = False, width: Optional[int] = None, height: Optional[int] = None, x: Optional[int] = None, y: Optional[int] = None, locale: bool = True, timeout: Optional[int] = None) -> Union[None, str]: ...
    @overload
    async def input_box(self, prompt: str = '', title: str = 'Input', default: str = '', hide: bool = False, width: Optional[int] = None, height: Optional[int] = None, x: Optional[int] = None, y: Optional[int] = None, locale: bool = True, timeout: Optional[int] = None, *, blocking: Literal[False]) -> Union[AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    @overload
    async def input_box(self, prompt: str = '', title: str = 'Input', default: str = '', hide: bool = False, width: Optional[int] = None, height: Optional[int] = None, x: Optional[int] = None, y: Optional[int] = None, locale: bool = True, timeout: Optional[int] = None, *, blocking: Literal[True]) -> Union[str, None]: ...
    @overload
    async def input_box(self, prompt: str = '', title: str = 'Input', default: str = '', hide: bool = False, width: Optional[int] = None, height: Optional[int] = None, x: Optional[int] = None, y: Optional[int] = None, locale: bool = True, timeout: Optional[int] = None, *, blocking: bool = True) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    # fmt: on
    async def input_box(
        self,
        prompt: str = '',
        title: str = 'Input',
        default: str = '',
        hide: bool = False,
        width: Optional[int] = None,
        height: Optional[int] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        locale: bool = True,
        timeout: Optional[int] = None,
        *,
        blocking: bool = True,
    ) -> Union[None, str, AsyncFutureResult[str], AsyncFutureResult[None]]:
        """
        Like AHK's ``InputBox``

        If the user presses Cancel or closes the box, ``None`` is returned.
        Otherwise, the user's input is returned.
        Raises a ``TimeoutError`` if a timeout is specified and expires.
        """
        args = [title, prompt]
        if hide:
            args.append('hide')
        else:
            args.append('')
        for opt in (width, height, x, y):
            if opt is not None:
                args.append(str(opt))
            else:
                args.append('')
        if locale:
            args.append('Locale')
        else:
            args.append('')
        if timeout is not None:
            args.append(str(timeout))
        else:
            args.append('')
        args.append(default)
        return await self._transport.function_call('AHKInputBox', args, blocking=blocking)

    # fmt: off
    @overload
    async def file_select_box(self, title: str = 'Select File', multi: bool = False, root: str = '', filter: str = '', save_button: bool = False, file_must_exist: bool = False, path_must_exist: bool = False, prompt_create_new_file: bool = False, prompt_override_file: bool = False, follow_shortcuts: bool = True) -> Union[None, str]: ...
    @overload
    async def file_select_box(self, title: str = 'Select File', multi: bool = False, root: str = '', filter: str = '', save_button: bool = False, file_must_exist: bool = False, path_must_exist: bool = False, prompt_create_new_file: bool = False, prompt_override_file: bool = False, follow_shortcuts: bool = True, *, blocking: Literal[False]) -> Union[AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    @overload
    async def file_select_box(self, title: str = 'Select File', multi: bool = False, root: str = '', filter: str = '', save_button: bool = False, file_must_exist: bool = False, path_must_exist: bool = False, prompt_create_new_file: bool = False, prompt_override_file: bool = False, follow_shortcuts: bool = True, *, blocking: Literal[True]) -> Union[str, None]: ...
    @overload
    async def file_select_box(self, title: str = 'Select File', multi: bool = False, root: str = '', filter: str = '', save_button: bool = False, file_must_exist: bool = False, path_must_exist: bool = False, prompt_create_new_file: bool = False, prompt_override_file: bool = False, follow_shortcuts: bool = True, *, blocking: bool = True) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    # fmt: on
    async def file_select_box(
        self,
        title: str = 'Select File',
        multi: bool = False,
        root: str = '',
        filter: str = '',
        save_button: bool = False,
        file_must_exist: bool = False,
        path_must_exist: bool = False,
        prompt_create_new_file: bool = False,
        prompt_override_file: bool = False,
        follow_shortcuts: bool = True,
        *,
        blocking: bool = True,
    ) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]:
        opts = 0
        if file_must_exist:
            opts += 1
        if path_must_exist:
            opts += 2
        if prompt_create_new_file:
            opts += 8
        if prompt_override_file:
            opts += 8
        if not follow_shortcuts:
            opts += 32
        options = ''
        if multi:
            options += 'M'
        if save_button:
            options += 'S'
        if opts:
            options += str(opts)
        args = [options, root, title, filter]
        return await self._transport.function_call('AHKFileSelectFile', args, blocking=blocking)

    # fmt: off
    @overload
    async def folder_select_box(self, prompt: str = 'Select Folder', root: str = '', chroot: bool = False, enable_new_directories: bool = True, edit_field: bool = False, new_dialog_style: bool = False) -> Union[None, str]: ...
    @overload
    async def folder_select_box(self, prompt: str = 'Select Folder', root: str = '', chroot: bool = False, enable_new_directories: bool = True, edit_field: bool = False, new_dialog_style: bool = False, *, blocking: Literal[False]) -> Union[AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    @overload
    async def folder_select_box(self, prompt: str = 'Select Folder', root: str = '', chroot: bool = False, enable_new_directories: bool = True, edit_field: bool = False, new_dialog_style: bool = False, *, blocking: Literal[True]) -> Union[str, None]: ...
    @overload
    async def folder_select_box(self, prompt: str = 'Select Folder', root: str = '', chroot: bool = False, enable_new_directories: bool = True, edit_field: bool = False, new_dialog_style: bool = False, *, blocking: bool = True) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]: ...
    # fmt: on
    async def folder_select_box(
        self,
        prompt: str = 'Select Folder',
        root: str = '',
        chroot: bool = False,
        enable_new_directories: bool = True,
        edit_field: bool = False,
        new_dialog_style: bool = False,
        *,
        blocking: bool = True,
    ) -> Union[str, None, AsyncFutureResult[str], AsyncFutureResult[None]]:
        if not chroot:
            starting_folder = '*'
        else:
            starting_folder = ''
        starting_folder += root
        if enable_new_directories:
            opts = 1
        else:
            opts = 0
        if edit_field:
            opts += 2
        if new_dialog_style:
            opts += 4
        args = [starting_folder, str(opts), prompt]
        return await self._transport.function_call('AHKFileSelectFolder', args, blocking=blocking)

    async def block_forever(self) -> NoReturn:
        """
        Blocks (sleeps) forever. Utility method to prevent script from exiting.
        """
        while True:
            await async_sleep(1)

    async def get_version(self) -> str:
        return await self._transport._get_full_version()

    async def get_major_version(self) -> Literal['v1', 'v2']:
        return await self._transport._get_major_version()
