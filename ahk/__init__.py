from typing import Any
from typing import Optional

from ._async import AsyncAHK
from ._async import AsyncControl
from ._async import AsyncWindow
from ._sync import AHK
from ._sync import Control
from ._sync import Window
from ._utils import MsgBoxButtons
from ._utils import MsgBoxDefaultButton
from ._utils import MsgBoxIcon
from ._utils import MsgBoxModality

__all__ = [
    'AHK',
    'Window',
    'AsyncWindow',
    'AsyncAHK',
    'Control',
    'AsyncControl',
    'MsgBoxButtons',
    'MsgBoxDefaultButton',
    'MsgBoxIcon',
    'MsgBoxModality',
]

_global_instance: Optional[AHK[None]] = None


def __getattr__(name: str) -> Any:
    global _global_instance
    if name in dir(AHK):
        if _global_instance is None:
            try:
                _global_instance = AHK()
            except EnvironmentError as init_error:
                raise EnvironmentError(
                    'Tried to create default global AHK instance, but it failed. This is most likely due to AutoHotkey.exe not being available on PATH or other default locations'
                ) from init_error
        return getattr(_global_instance, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
