from collections import deque
from typing import Optional
from typing import Tuple

from .transport import AsyncDaemonProcessTransport
from .transport import AsyncTransport
from .window import AsyncWindow


class AsyncAHK:
    def __init__(self, transport: Optional[AsyncTransport] = None):
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
