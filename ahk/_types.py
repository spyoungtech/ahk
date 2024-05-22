from __future__ import annotations

import sys
from typing import Literal
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias


class Position(NamedTuple):
    x: int
    y: int
    width: int
    height: int


class Coordinates(NamedTuple):
    x: int
    y: int


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

SendMode: TypeAlias = Literal['Event', 'Input', 'InputThenPlay', 'Play', '']

FunctionName = Literal[
    'AHKBlockInput',
    'AHKClipWait',
    'AHKControlClick',
    'AHKControlGetPos',
    'AHKControlGetText',
    'AHKControlSend',
    'AHKFileSelectFile',
    'AHKFileSelectFolder',
    'AHKGetClipboard',
    'AHKGetClipboardAll',
    'AHKGetCoordMode',
    'AHKGetSendLevel',
    'AHKGetSendMode',
    'AHKGetTitleMatchMode',
    'AHKGetTitleMatchSpeed',
    'AHKGetVolume',
    'AHKGuiNew',
    'AHKImageSearch',
    'AHKInputBox',
    'AHKKeyState',
    'AHKKeyWait',
    'AHKMenuTrayIcon',
    'AHKMenuTrayShow',
    'AHKMenuTrayHide',
    'AHKMenuTrayTip',
    'AHKMsgBox',
    'AHKMouseClickDrag',
    'AHKMouseGetPos',
    'AHKMouseMove',
    'AHKPixelGetColor',
    'AHKPixelSearch',
    'AHKRegRead',
    'AHKRegWrite',
    'AHKRegDelete',
    'AHKSend',
    'AHKSendEvent',
    'AHKSendInput',
    'AHKSendPlay',
    'AHKSendRaw',
    'AHKSetClipboard',
    'AHKSetClipboardAll',
    'AHKSetCoordMode',
    'AHKSetDetectHiddenWindows',
    'AHKSetSendLevel',
    'AHKSetSendMode',
    'AHKSetTitleMatchMode',
    'AHKSetVolume',
    'AHKShowToolTip',
    'AHKSoundBeep',
    'AHKSoundGet',
    'AHKSoundPlay',
    'AHKSoundSet',
    'AHKTrayTip',
    'AHKWinActivate',
    'AHKWinClose',
    'AHKWinExist',
    'AHKWinFromMouse',
    'AHKWinGetControlList',
    'AHKWinGetControlListHwnd',
    'AHKWinGetCount',
    'AHKWinGetExStyle',
    'AHKWinGetID',
    'AHKWinGetIDLast',
    'AHKWinGetList',
    'AHKWinGetMinMax',
    'AHKWinGetPID',
    'AHKWinGetPos',
    'AHKWinGetProcessName',
    'AHKWinGetProcessPath',
    'AHKWinGetStyle',
    'AHKWinGetText',
    'AHKWinGetTitle',
    'AHKWinGetTransColor',
    'AHKWinGetTransparent',
    'AHKWinHide',
    'AHKWinIsActive',
    'AHKWinIsAlwaysOnTop',
    'AHKWinMove',
    'AHKWinSetAlwaysOnTop',
    'AHKWinSetBottom',
    'AHKWinSetDisable',
    'AHKWinSetEnable',
    'AHKWinSetExStyle',
    'AHKWinSetRedraw',
    'AHKWinSetRegion',
    'AHKWinSetStyle',
    'AHKWinSetTitle',
    'AHKWinSetTop',
    'AHKWinSetTransColor',
    'AHKWinSetTransparent',
    'AHKWinShow',
    'AHKWindowList',
    'AHKWinWait',
    'AHKWinWaitActive',
    'AHKWinWaitClose',
    'AHKWinWaitNotActive',
    'AHKClick',
    'AHKSetCapsLockState',
    'AHKSetNumLockState',
    'AHKSetScrollLockState',
    'SetKeyDelay',
    'WinActivateBottom',
    'AHKWinGetClass',
    'AHKWinKill',
    'AHKWinMaximize',
    'AHKWinMinimize',
    'AHKWinRestore',
]
