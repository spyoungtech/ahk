from collections import deque
from typing import Optional
from typing import Tuple

from .transport import DaemonProcessTransport
from .transport import Transport
from .window import Window


class AHK:
    def __init__(self, transport: Optional[Transport] = None):
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
