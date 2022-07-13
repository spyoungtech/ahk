import typing
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

from .transport import AsyncDaemonProcessTransport
from .transport import AsyncTransport
from .window import AsyncWindow


class FutureResult:
    ...


class AsyncAHK:
    def __init__(self, *, transport: Optional[AsyncTransport] = None):
        if transport is None:
            transport = AsyncDaemonProcessTransport()
        self._transport: AsyncTransport = transport

    async def list_windows(self) -> list[AsyncWindow]:
        resp = await self._transport.function_call('WindowList')
        window_ids = resp.unpack()
        ret = [AsyncWindow(engine=self, ahk_id=ahk_id) for ahk_id in window_ids]
        return ret

    async def get_mouse_position(self) -> Tuple[int, int]:
        resp = await self._transport.function_call('MouseGetPos')
        return resp.unpack()

    @typing.overload
    async def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        speed: Optional[int] = None,
        relative: bool = False,
    ) -> None:
        ...

    @typing.overload
    async def mouse_move(
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
    async def mouse_move(
        self,
        x: Optional[Union[str, int]] = None,
        y: Optional[Union[str, int]] = None,
        *,
        blocking: Literal[False],
        speed: Optional[int] = None,
        relative: bool = False,
    ) -> FutureResult:
        ...

    async def mouse_move(
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
            posx, posy = await self.get_mouse_position()
            x = x or posx
            y = y or posy

        if speed is None:
            speed = 2
        args = [str(x), str(y), str(speed)]
        if relative:
            args.append('R')
        if blocking in (True, None):
            resp = await self._transport.function_call('MouseMove', args)
            resp.unpack()
            return None
        elif blocking is False:
            return FutureResult()
        else:
            raise ValueError(f'Invalid value for argument blocking: {blocking!r}')
