from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Iterable
from typing import Literal
from typing import Optional
from typing import overload
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from ..message import IntegerResponseMessage
from ..message import is_winget_response_type
from ..message import StringResponseMessage
from ..message import WindowControlListResponseMessage
from ..message import WindowIDListResponseMessage
from .transport import DaemonProcessTransport
from .transport import Transport
from .window import SyncControl
from .window import Window


class FutureResult:
    ...


CoordModeTargets = Union[Literal['ToolTip'], Literal['Pixel'], Literal['Mouse'], Literal['Caret'], Literal['Menu']]
CoordModeRelativeTo = Union[Literal['Screen'], Literal['Relative'], Literal['Window'], Literal['Client']]
WinGetFunctions = Literal[
    Literal['WinGetID'],
    Literal['WinGetIDLast'],
    Literal['WinGetPID'],
    Literal['WinGetProcessName'],
    Literal['WinGetProcessPath'],
    Literal['WinGetCount'],
    Literal['WinGetList'],
    Literal['WinGetMinMax'],
    Literal['WinGetControlList'],
    Literal['WinGetControlListHwnd'],
    Literal['WinGetTransparent'],
    Literal['WinGetTransColor'],
    Literal['WinGetStyle'],
    Literal['WinGetExStyle'],
]
CoordMode = Union[CoordModeTargets, Tuple[CoordModeTargets, CoordModeRelativeTo]]


class AHK:
    def __init__(self, *, TransportClass: Optional[Type[Transport]] = None, **transport_kwargs: Any):
        if TransportClass is None:
            TransportClass = DaemonProcessTransport
        assert TransportClass is not None
        transport = TransportClass(**transport_kwargs)
        self._transport: Transport = transport

    def list_windows(self) -> list[Window]:
        resp = self._transport.function_call('WindowList')
        window_ids = resp.unpack()
        ret = [Window(engine=self, ahk_id=ahk_id) for ahk_id in window_ids]
        return ret

    def get_mouse_position(self) -> Tuple[int, int]:
        resp = self._transport.function_call('MouseGetPos')
        return resp.unpack()

    @overload
    def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        speed: Optional[int] = None,
        relative: bool = False,
    ) -> None:
        ...

    @overload
    def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        blocking: Literal[True],
        speed: Optional[int] = None,
        relative: bool = False,
    ) -> None:
        ...

    @overload
    def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        blocking: Literal[False],
        speed: Optional[int] = None,
        relative: bool = False,
    ) -> FutureResult:
        ...

    def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        speed: Optional[int] = None,
        relative: bool = False,
        blocking: Optional[Union[Literal[True], Literal[False]]] = None,
    ) -> Union[None, FutureResult]:
        if relative and (x is None or y is None):
            x = x or 0
            y = y or 0
        elif not relative and (x is None or y is None):
            posx, posy = self.get_mouse_position()
            x = x or posx
            y = y or posy

        if speed is None:
            speed = 2
        args = [str(x), str(y), str(speed)]
        if relative:
            args.append('R')
        if blocking in (True, None):
            resp = self._transport.function_call('MouseMove', args)
            resp.unpack()
            return None
        elif blocking is False:
            return FutureResult()
        else:
            raise ValueError(f'Invalid value for argument blocking: {blocking!r}')

    def a_run_script(self, script_text: str, decode: bool = True, blocking: bool = True, **runkwargs: Any) -> str:
        raise NotImplementedError()

    def get_active_window(self) -> Union[Window, None]:
        raise NotImplementedError()

    def find_windows(
        self, func: Optional[Callable[[Window], bool]] = None, **kwargs: Any
    ) -> Iterable[Window]:
        raise NotImplementedError()

    def find_windows_by_class(self, class_name: str, exact: bool = False) -> Iterable[Window]:
        raise NotImplementedError()

    def find_windows_by_text(self, text: str, exact: bool = False) -> Iterable[Window]:
        raise NotImplementedError()

    def find_windows_by_title(self, title: str, exact: bool = False) -> Iterable[Window]:
        raise NotImplementedError()

    def get_volume(self, device_number: int = 1) -> float:
        raise NotImplementedError()

    def key_down(self, key: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    def key_press(self, key: str, release: bool = True, blocking: bool = True) -> None:
        raise NotImplementedError()

    def key_release(self, key: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    def key_state(self, key_name: str, mode: Optional[Union[Literal['P'], Literal['T']]] = None) -> bool:
        raise NotImplementedError()

    def key_up(self, key: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    def key_wait(
        self, key_name: str, timeout: Optional[int] = None, logical_state: bool = False, released: bool = False
    ) -> None:
        raise NotImplementedError()

    # async def mouse_position(self):
    #     raise NotImplementedError()

    def mouse_wheel(
        self,
        direction: Union[
            Literal['up'], Literal['down'], Literal['UP'], Literal['DOWN'], Literal['Up'], Literal['Down']
        ],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError()

    # async def reg_delete(self, key_name: str, value_name: str = '') -> None:
    #     raise NotImplementedError()
    #
    # async def reg_loop(self, reg: str, key_name: str, mode=''):
    #     raise NotImplementedError()
    #
    # async def reg_read(self, key_name: str, value_name='') -> str:
    #     raise NotImplementedError()
    #
    # async def reg_set_view(self, reg_view: int) -> None:
    #     raise NotImplementedError()
    #
    # async def reg_write(self, value_type: str, key_name: str, value_name='') -> None:
    #     raise NotImplementedError()

    def run_script(self, script_text: str, decode: bool = True, blocking: bool = True, **runkwargs: Any) -> str:
        raise NotImplementedError()

    def send(self, s: str, raw: bool = False, delay: Optional[int] = None, blocking: bool = True) -> None:
        raise NotImplementedError()

    def send_event(self, s: str, delay: Optional[int] = None) -> None:
        raise NotImplementedError()

    def send_input(self, s: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    def send_play(self, s: str) -> None:
        raise NotImplementedError()

    def send_raw(self, s: str, delay: Optional[int] = None) -> None:
        raise NotImplementedError()

    def set_capslock_state(
        self, state: Optional[Union[Literal['On'], Literal['Off'], Literal['AlwaysOn'], Literal['AlwaysOff']]] = None
    ) -> None:
        raise NotImplementedError()

    def set_volume(self, value: int, device_number: int = 1) -> None:
        raise NotImplementedError()

    def show_error_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        slient: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    def show_info_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        slient: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    def show_tooltip(
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

    def show_warning_traytip(
        self,
        title: str,
        text: str,
        second: float = 1.0,
        slient: bool = False,
        large_icon: bool = False,
        blocking: bool = True,
    ) -> None:
        raise NotImplementedError()

    def sound_beep(self, frequency: int = 523, duration: int = 150) -> None:
        raise NotImplementedError()

    def sound_get(
        self, device_number: int = 1, component_type: str = 'MASTER', control_type: str = 'VOLUME'
    ) -> None:
        raise NotImplementedError()

    def sound_play(self, filename: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    def sound_set(
        self,
        value: Union[str, int, float],
        device_number: int = 1,
        component_type: str = 'MASTER',
        control_type: str = 'VOLUME',
    ) -> None:
        raise NotImplementedError()

    def type(self, s: str, blocking: bool = True) -> None:
        raise NotImplementedError()

    # fmt: off
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetID'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetIDLast'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetPID'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> IntegerResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetProcessName'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetProcessPath'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetCount'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> IntegerResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetList'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> WindowIDListResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetMinMax'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> IntegerResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetControlList'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> WindowControlListResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetControlListHwnd'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> WindowControlListResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetTransparent'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> IntegerResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetTransColor'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetStyle'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    @overload
    def _win_get(self, subcommand_function: Literal['WinGetExStyle'], /, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = '') -> StringResponseMessage: ...
    # fmt: on

    def _win_get(
        self,
        subcommand_function: WinGetFunctions,
        /,
        title: str = '',
        text: str = '',
        exclude_title: str = '',
        exclude_text: str = '',
    ) -> Union[
        StringResponseMessage,
        IntegerResponseMessage,
        WindowIDListResponseMessage,
        WindowControlListResponseMessage,
    ]:

        args = [title, text, exclude_title, exclude_title, exclude_text]
        resp = self._transport.function_call(subcommand_function, args)
        assert is_winget_response_type(resp)
        return resp

    def win_get(
        self, title: str = '', text: str = '', exclude_title: str = '', exclude_text: str = ''
    ) -> Window:
        resp = self._win_get(
            'WinGetID', title=title, text=text, exclude_title=exclude_title, exclude_text=exclude_text
        )
        win_id = resp.unpack()
        return Window(engine=self, ahk_id=win_id)

    def win_set(self, subcommand: str, *args: Any, blocking: bool = True) -> None:
        # TODO: type hint subcommand literals
        raise NotImplementedError()

    def windows(self) -> Sequence[Window]:
        raise NotImplementedError()

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        *,
        button: Optional[str] = None,
        n: Optional[int] = None,
        direction: Optional[str] = None,
        relative: Optional[bool] = None,
        blocking: bool = True,
        mode: Optional[CoordMode] = None,
    ) -> None:
        raise NotImplementedError()

    def image_search(
        self,
        image_path: str,
        upper_bound: Tuple[Union[int, str], Union[int, str]] = (0, 0),
        lower_bound: Optional[Tuple[Union[int, str], Union[int, str]]] = None,
        *,
        color_variation: Optional[int] = None,
        coord_mode: str = 'Screen',
        scale_height: Optional[int] = None,
        scale_width: Optional[int] = None,
        transparent: Optional[str] = None,
        icon: Optional[int] = None,
    ) -> Union[Tuple[int, int], None]:
        """
        https://www.autohotkey.com/docs/commands/ImageSearch.htm
        """

        if scale_height and not scale_width:
            scale_width = -1
        elif scale_width and not scale_height:
            scale_height = -1

        options: list[Union[str, int]] = []
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

        args = [
            str(x1),
            str(y1),
            str(x2),
            str(y2),
        ]
        if options:
            s = ''
            for opt in options:
                s += f'*{opt} '
            s += image_path
            args.append(s)
        else:
            args.append(image_path)
        resp = self._transport.function_call('ImageSearch', args)
        return resp.unpack()

    def mouse_drag(
        self,
        x: int,
        y: Optional[int] = None,
        *,
        from_position: Optional[Tuple[int, int]] = None,
        speed: Optional[int] = None,
        button: Union[str, int] = 1,
        relative: Optional[bool] = None,
        blocking: bool = True,
        mode: Optional[CoordMode] = None,
    ) -> None:
        raise NotImplementedError()

    def pixel_get_color(
        self, x: int, y: int, coord_mode: str = 'Screen', alt: bool = False, slow: bool = False, rgb: bool = True
    ) -> str:
        raise NotImplementedError()

    def pixel_search(
        self,
        color: Union[str, int],
        variation: int = 0,
        upper_bound: Tuple[int, int] = (0, 0),
        lower_bound: Optional[Tuple[int, int]] = None,
        coord_mode: str = 'Screen',
        fast: bool = True,
        rgb: bool = True,
    ) -> Union[Tuple[int, int], None]:
        raise NotImplementedError()

    def show_traytip(
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

    def win_close(
        self,
        title: Optional[str] = None,
        *,
        text: Optional[str] = None,
        seconds_to_wait: Optional[int] = None,
        exclude_title: Optional[str] = None,
        exclude_text: Optional[str] = None,
    ) -> None:
        args = []
        optional_args = (text, seconds_to_wait, exclude_title, exclude_text)
        if title is not None:
            args.append(title)
        if any(optional_args):
            for arg in optional_args:
                args.append(str(arg) or '')
        resp = self._transport.function_call('WinClose', args=args)
        resp.unpack()
        return None
