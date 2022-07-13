import typing
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

from .transport import DaemonProcessTransport
from .transport import Transport
from .window import Window


class FutureResult:
    ...


class AHK:
    def __init__(self, *, transport: Optional[Transport] = None):
        if transport is None:
            transport = DaemonProcessTransport()
        self._transport: Transport = transport

    def list_windows(self) -> list[Window]:
        resp = self._transport.function_call('WindowList')
        window_ids = resp.unpack()
        ret = [Window(engine=self, ahk_id=ahk_id) for ahk_id in window_ids]
        return ret

    def get_mouse_position(self) -> Tuple[int, int]:
        resp = self._transport.function_call('MouseGetPos')
        return resp.unpack()

    @typing.overload
    def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        speed: Optional[int] = None,
        relative: bool = False,
    ) -> None:
        ...

    @typing.overload
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

    @typing.overload
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
