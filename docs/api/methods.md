# Available Methods

Most useful methods from autohotkey are implemented in this wrapper. However, not everything is implemented (yet). This
page can serve as a quick reference of AutoHotkey methods that are implemented in the wrapper.

(Coming soon: links to equivalent Python method(s))

### Mouse and Keyboard

| AutoHotkey Command                                                                           | Status          | Notes                                                                   |
|----------------------------------------------------------------------------------------------|-----------------|-------------------------------------------------------------------------|
| [#KeyHistory](https://www.autohotkey.com/docs/commands/_KeyHistory.htm)                      | Not Implemented |                                                                         |
| [BlockInput](https://www.autohotkey.com/docs/commands/BlockInput.htm)                        | Implemented     |                                                                         |
| [Click](https://www.autohotkey.com/docs/commands/Click.htm)                                  | Implemented     |                                                                         |
| [ControlClick](https://www.autohotkey.com/docs/commands/ControlClick.htm)                    | Implemented     |                                                                         |
| [ControlSend[Raw]](https://www.autohotkey.com/docs/commands/ControlSend.htm)                 | Implemented     |                                                                         |
| [CoordMode](https://www.autohotkey.com/docs/commands/CoordMode.htm)                          | Implemented     |                                                                         |
| [GetKeyName()](https://www.autohotkey.com/docs/commands/GetKey.htm)                          | Not Implemented |                                                                         |
| [GetKeySC()](https://www.autohotkey.com/docs/commands/GetKey.htm)                            | Not Implemented |                                                                         |
| [GetKeyState](https://www.autohotkey.com/docs/commands/GetKeyState.htm#command)              | Implemented     |                                                                         |
| [GetKeyVK()](https://www.autohotkey.com/docs/commands/GetKey.htm)                            | Not Implemented |                                                                         |
| [KeyHistory](https://www.autohotkey.com/docs/commands/KeyHistory.htm)                        | Not Implemented |                                                                         |
| [KeyWait](https://www.autohotkey.com/docs/commands/KeyWait.htm)                              | Implemented     |                                                                         |
| [Input](https://www.autohotkey.com/docs/commands/Input.htm)                                  | Not Implemented | Use python `input()` instead                                            |
| [InputHook()](https://www.autohotkey.com/docs/commands/InputHook.htm)                        | Not Implemented |                                                                         |
| [MouseClick](https://www.autohotkey.com/docs/commands/MouseClick.htm)                        | Implemented     |                                                                         |
| [MouseClickDrag](https://www.autohotkey.com/docs/commands/MouseClickDrag.htm)                | Implemented     |                                                                         |
| [MouseGetPos](https://www.autohotkey.com/docs/commands/MouseGetPos.htm)                      | Implemented     |                                                                         |
| [MouseMove](https://www.autohotkey.com/docs/commands/MouseMove.htm)                          | Implemented     |                                                                         |
| [SendLevel](https://www.autohotkey.com/docs/commands/SendLevel.htm)                          | Implemented     |                                                                         |
| [SendMode](https://www.autohotkey.com/docs/commands/SendMode.htm)                            | Not Implemented |                                                                         |
| [SetCapsLockState](https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm)   | Implemented     |                                                                         |
| [SetDefaultMouseSpeed](https://www.autohotkey.com/docs/commands/SetDefaultMouseSpeed.htm)    | Implemented     | Speed is controlled by the `speed` keyword argument of relevant methods |
| [SetKeyDelay](https://www.autohotkey.com/docs/commands/SetKeyDelay.htm)                      | Implemented     | Delay is controlled by the `delay` keyword argument of relevant methods |
| [SetMouseDelay](https://www.autohotkey.com/docs/commands/SetMouseDelay.htm)                  | Not Implemented | Delays between mouse movements can be controlled in Python code         |
| [SetNumLockState](https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm)    | Implemented     |                                                                         |
| [SetScrollLockState](https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm) | Implemented     |                                                                         |
| [SetStoreCapsLockMode](https://www.autohotkey.com/docs/commands/SetStoreCapslockMode.htm)    | Not Implemented | note                                                                    |


### Hotkeys

| AutoHotkey Command                                              | Status       | Notes                                                                                                                              |
|-----------------------------------------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------|
| [Hotkeys](https://www.autohotkey.com/docs/Hotkeys.htm)          | Implemented  | Before 1.0, callbacks were only supported as Autohotkey Scripts<br/> In 1.0 and later, callbacks are supported as Python functions |
| [Hotstrings](https://www.autohotkey.com/docs/Hotstrings.htm)    | Implemented  | Available in 1.0+                                                                                                                  |
| [Suspend](https://www.autohotkey.com/docs/commands/Suspend.htm) | Implemented* | Use stop_hotkeys and start_hotkeys to enable/disable hotkeys                                                                       |



### ClipBoard

| AutoHotkey Command                                                                             | Status      | Notes |
|------------------------------------------------------------------------------------------------|-------------|-------|
| [OnClipboardChange()](https://www.autohotkey.com/docs/commands/OnClipboardChange.htm#function) | Implemented |       |
| [Clipboard/ClipboardAll](https://www.autohotkey.com/docs/misc/Clipboard.htm#ClipboardAll)      | Implemented |       |
| [ClipWAit](https://www.autohotkey.com/docs/v1/lib/ClipWait.htm)                                | Implemented | note  |



### Screen/Image

| AutoHotkey Command                                                                           | Status      | Notes |
|----------------------------------------------------------------------------------------------|-------------|-------|
| [ImageSearch](https://www.autohotkey.com/docs/commands/ImageSearch.htm)                      | Implemented |       |
| [PixelGetColor](https://www.autohotkey.com/docs/commands/PixelGetColor.htm)                  | Implemented |       |
| [PixelSearch](https://www.autohotkey.com/docs/commands/PixelSearch.htm)                      | Implemented | note  |


### Registry



| AutoHotkey Command                                                                           | Status          | Notes |
|----------------------------------------------------------------------------------------------|-----------------|-------|
| [RegDelete](https://www.autohotkey.com/docs/commands/RegDelete.htm)                          | Implemented     |       |
| [RegRead](https://www.autohotkey.com/docs/commands/RegRead.htm)                              | Implemented     |       |
| [RegWrite](https://www.autohotkey.com/docs/commands/RegWrite.htm)                            | Implemented     |       |
| [SetRegView](https://www.autohotkey.com/docs/commands/SetRegView.htm)                        | Not Implemented | note  |



### Window


#### Window | Controls

| AutoHotkey Command                                                                           | Status          | Notes |
|----------------------------------------------------------------------------------------------|-----------------|-------|
| [Control](https://www.autohotkey.com/docs/commands/Control.htm)                              | Implemented     |       |
| [ControlClick](https://www.autohotkey.com/docs/commands/ControlClick.htm)                    | Implemented     |       |
| [ControlFocus](https://www.autohotkey.com/docs/commands/ControlFocus.htm)                    | Not Implemented |       |
| [ControlGet](https://www.autohotkey.com/docs/commands/ControlGet.htm)                        | Implemented     |       |
| [ControlGetFocus](https://www.autohotkey.com/docs/commands/ControlGetFocus.htm)              | Not Implemented |       |
| [ControlGetPos](https://www.autohotkey.com/docs/commands/ControlGetPos.htm)                  | Implemented     |       |
| [ControlGetText](https://www.autohotkey.com/docs/commands/ControlGetText.htm)                | Implemented     |       |
| [ControlMove](https://www.autohotkey.com/docs/commands/ControlMove.htm)                      | Implemented     |       |
| [ControlSend[Raw]](https://www.autohotkey.com/docs/commands/ControlSend.htm)                 | Implemented     |       |
| [ControlSetText](https://www.autohotkey.com/docs/commands/ControlSetText.htm)                | Implemented     |       |
| [Menu](https://www.autohotkey.com/docs/commands/Menu.htm)                                    | Not Implemented |       |
| [PostMessage/SendMessage](https://www.autohotkey.com/docs/commands/PostMessage.htm)          | Not Implemented |       |
| [SetControlDelay](https://www.autohotkey.com/docs/commands/SetControlDelay.htm)              | Not Implemented |       |
| [WinMenuSelectItem](https://www.autohotkey.com/docs/commands/WinMenuSelectItem.htm)          | Not Implemented | note  |


#### Window | Groups

| AutoHotkey Command                                                                           | Status          | Notes |
|----------------------------------------------------------------------------------------------|-----------------|-------|
| [GroupActivate](https://www.autohotkey.com/docs/commands/GroupActivate.htm)                  |                 |       |
| [GroupAdd](https://www.autohotkey.com/docs/commands/GroupAdd.htm)                            |                 |       |
| [GroupClose](https://www.autohotkey.com/docs/commands/GroupClose.htm)                        |                 |       |
| [GroupDeactivate](https://www.autohotkey.com/docs/commands/GroupDeactivate.htm)              |                 | note  |

### Window functions

| AutoHotkey Command                                                                      | Status          | Notes                                             |
|-----------------------------------------------------------------------------------------|-----------------|---------------------------------------------------|
| [#WinActivateForce](https://www.autohotkey.com/docs/commands/_WinActivateForce.htm)     | Implemented     | Any directive can be added to the daemon          |
| [DetectHiddenText](https://www.autohotkey.com/docs/commands/DetectHiddenText.htm)       | Planned         |                                                   |
| [DetectHiddenWindows](https://www.autohotkey.com/docs/commands/DetectHiddenWindows.htm) | Implemented     |                                                   |
| [IfWin[Not]Active](https://www.autohotkey.com/docs/commands/IfWinActive.htm)            | Not Implemented | Use Python `if` with `win_active`/`win.is_active` |
| [IfWin[Not]Exist](https://www.autohotkey.com/docs/commands/IfWinExist.htm)              | Not Implemented | Use Python `if` with `win_exists`/`win.exists`    |
| [SetTitleMatchMode](https://www.autohotkey.com/docs/commands/SetTitleMatchMode.htm)     | Implemented     |                                                   |
| [SetWinDelay](https://www.autohotkey.com/docs/commands/SetWinDelay.htm)                 | Not Implemented | Delays can be controlled in Python code           |
| [StatusBarGetText](https://www.autohotkey.com/docs/commands/StatusBarGetText.htm)       | Not Implemented |                                                   |
| [StatusBarWait](https://www.autohotkey.com/docs/commands/StatusBarWait.htm)             | Not Implemented |                                                   |
| [WinActivate](https://www.autohotkey.com/docs/commands/WinActivate.htm)                 | Implemented     |                                                   |
| [WinActivateBottom](https://www.autohotkey.com/docs/commands/WinActivateBottom.htm)     | Implemented     |                                                   |
| [WinActive()](https://www.autohotkey.com/docs/commands/WinActive.htm)                   | Implemented     |                                                   |
| [WinClose](https://www.autohotkey.com/docs/commands/WinClose.htm)                       | Implemented     |                                                   |
| [WinExist()](https://www.autohotkey.com/docs/commands/WinExist.htm)                     | Implemented     |                                                   |
| [WinGet](https://www.autohotkey.com/docs/commands/WinGet.htm)                           | Implemented     |                                                   |
| [WinGetActiveStats](https://www.autohotkey.com/docs/commands/WinGetActiveStats.htm)     | Not Implemented |                                                   |
| [WinGetActiveTitle](https://www.autohotkey.com/docs/commands/WinGetActiveTitle.htm)     | Not Implemented |                                                   |
| [WinGetClass](https://www.autohotkey.com/docs/commands/WinGetClass.htm)                 | Implemented     |                                                   |
| [WinGetPos](https://www.autohotkey.com/docs/commands/WinGetPos.htm)                     | Implemented     |                                                   |
| [WinGetText](https://www.autohotkey.com/docs/commands/WinGetText.htm)                   | Implemented     |                                                   |
| [WinGetTitle](https://www.autohotkey.com/docs/commands/WinGetTitle.htm)                 | Implemented     |                                                   |
| [WinHide](https://www.autohotkey.com/docs/commands/WinHide.htm)                         | Implemented     |                                                   |
| [WinKill](https://www.autohotkey.com/docs/commands/WinKill.htm)                         | Implemented     |                                                   |
| [WinMaximize](https://www.autohotkey.com/docs/commands/WinMaximize.htm)                 | Implemented     |                                                   |
| [WinMinimize](https://www.autohotkey.com/docs/commands/WinMinimize.htm)                 | Implemented     |                                                   |
| [WinMinimizeAll[Undo]](https://www.autohotkey.com/docs/commands/WinMinimizeAll.htm)     | Not Implemented |                                                   |
| [WinMove](https://www.autohotkey.com/docs/commands/WinMove.htm)                         | Implemented     |                                                   |
| [WinRestore](https://www.autohotkey.com/docs/commands/WinRestore.htm)                   | Implemented     |                                                   |
| [WinSet](https://www.autohotkey.com/docs/commands/WinSet.htm)                           | Implemented     |                                                   |
| [WinSetTitle](https://www.autohotkey.com/docs/commands/WinSetTitle.htm)                 | Implemented     |                                                   |
| [WinShow](https://www.autohotkey.com/docs/commands/WinShow.htm)                         | Implemented     |                                                   |
| [WinWait](https://www.autohotkey.com/docs/commands/WinWait.htm)                         | Implemented     |                                                   |
| [WinWait[Not]Active](https://www.autohotkey.com/docs/commands/WinWaitActive.htm)        | Implemented     |                                                   |
| [WinWaitClose](https://www.autohotkey.com/docs/commands/WinWaitClose.htm)               | Implemented     | note                                              |




### Sound

| AutoHotkey Command                                                                           | Status          | Notes |
|----------------------------------------------------------------------------------------------|-----------------|-------|
| [SoundBeep](https://www.autohotkey.com/docs/commands/SoundBeep.htm)                          | Implemented     |       |
| [SoundGet](https://www.autohotkey.com/docs/commands/SoundGet.htm)                            | Implemented     |       |
| [SoundGetWaveVolume](https://www.autohotkey.com/docs/commands/SoundGetWaveVolume.htm)        | Not Implemented |       |
| [SoundPlay](https://www.autohotkey.com/docs/commands/SoundPlay.htm)                          | Implemented     |       |
| [SoundSet](https://www.autohotkey.com/docs/commands/SoundSet.htm)                            | Implemented     |       |
| [SoundSetWaveVolume](https://www.autohotkey.com/docs/commands/SoundSetWaveVolume.htm)        | Not Implemented | note  |



### GUI

GUI methods are largely unimplmented, except `ToolTip` and `TrayTip`.
We recommend using one of the many Python GUI libraries, such as [easygui](https://github.com/robertlugg/easygui), [pysimplegui](https://www.pysimplegui.org/en/latest/) or similar.


| AutoHotkey Command                                                            | Status          | Notes |
|-------------------------------------------------------------------------------|-----------------|-------|
| [Gui](https://www.autohotkey.com/docs/commands/Gui.htm)                       | Not Implemented |       |
| [Gui control types](https://www.autohotkey.com/docs/commands/GuiControls.htm) | Not Implemented |       |
| [GuiControl](https://www.autohotkey.com/docs/commands/GuiControl.htm)         | Not Implemented |       |
| [GuiControlGet](https://www.autohotkey.com/docs/commands/GuiControlGet.htm)   | Not Implemented |       |
| [Gui ListView control](https://www.autohotkey.com/docs/commands/ListView.htm) | Not Implemented |       |
| [Gui TreeView control](https://www.autohotkey.com/docs/commands/TreeView.htm) | Not Implemented |       |
| [IfMsgBox](https://www.autohotkey.com/docs/commands/IfMsgBox.htm)             | Not Implemented |       |
| [InputBox](https://www.autohotkey.com/docs/commands/InputBox.htm)             | Not Implemented |       |
| [LoadPicture()](https://www.autohotkey.com/docs/commands/LoadPicture.htm)     | Not Implemented |       |
| [Menu](https://www.autohotkey.com/docs/commands/Menu.htm)                     | Not Implemented |       |
| [MenuGetHandle()](https://www.autohotkey.com/docs/commands/MenuGetHandle.htm) | Not Implemented |       |
| [MenuGetName()](https://www.autohotkey.com/docs/commands/MenuGetName.htm)     | Not Implemented |       |
| [MsgBox](https://www.autohotkey.com/docs/commands/MsgBox.htm)                 | Not Implemented |       |
| [OnMessage()](https://www.autohotkey.com/docs/commands/OnMessage.htm)         | Not Implemented |       |
| [Progress](https://www.autohotkey.com/docs/commands/Progress.htm)             | Not Implemented |       |
| [SplashImage](https://www.autohotkey.com/docs/commands/Progress.htm)          | Not Implemented |       |
| [SplashTextOn/Off](https://www.autohotkey.com/docs/commands/SplashTextOn.htm) | Not Implemented |       |
| [ToolTip](https://www.autohotkey.com/docs/commands/ToolTip.htm)               | Implemented     |       |
| [TrayTip](https://www.autohotkey.com/docs/commands/TrayTip.htm)               | Implemented     | note  |



### Directives

In general, all directives are technically usable, however many do not have applicable context in the Python library.

Some directives are mentioned in tables above and are omitted from this table.

| AutoHotkey Command                                                                            | Notes                                                                                                            |
|-----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| [#HotkeyInterval](https://www.autohotkey.com/docs/commands/_HotkeyInterval.htm)               |                                                                                                                  |
| [#HotkeyModifierTimeout](https://www.autohotkey.com/docs/commands/_HotkeyModifierTimeout.htm) |                                                                                                                  |
| [#Hotstring](https://www.autohotkey.com/docs/commands/_Hotstring.htm)                         |                                                                                                                  |
| [#Include[Again]](https://www.autohotkey.com/docs/commands/_Include.htm)                      | Using this directive is strongly discouraged as it is **very** likely to cause issues. Use with extreme caution. |
| [#InputLevel](https://www.autohotkey.com/docs/commands/_InputLevel.htm)                       |                                                                                                                  |
| [#KeyHistory](https://www.autohotkey.com/docs/commands/_KeyHistory.htm)                       |                                                                                                                  |
| [#MaxHotkeysPerInterval](https://www.autohotkey.com/docs/commands/_MaxHotkeysPerInterval.htm) |                                                                                                                  |
| [#MaxMem](https://www.autohotkey.com/docs/commands/_MaxMem.htm)                               |                                                                                                                  |
| [#MaxThreads](https://www.autohotkey.com/docs/commands/_MaxThreads.htm)                       |                                                                                                                  |
| [#MaxThreadsBuffer](https://www.autohotkey.com/docs/commands/_MaxThreadsBuffer.htm)           |                                                                                                                  |
| [#MaxThreadsPerHotkey](https://www.autohotkey.com/docs/commands/_MaxThreadsPerHotkey.htm)     | Hotkey callbacks are run in Python, so this largely won't have any significant effect                            |
| [#MenuMaskKey](https://www.autohotkey.com/docs/commands/_MenuMaskKey.htm)                     |                                                                                                                  |
| [#NoEnv](https://www.autohotkey.com/docs/commands/_NoEnv.htm)                                 |                                                                                                                  |
| [#NoTrayIcon](https://www.autohotkey.com/docs/commands/_NoTrayIcon.htm)                       | If you use hotkeys or hotstrings, you probably also want to configure this as a hotkey transport option          |
| [#Persistent](https://www.autohotkey.com/docs/commands/_Persistent.htm)                       | This is on by default in scripts run by this library                                                             |
| [#Requires](https://www.autohotkey.com/docs/commands/_Requires.htm)                           |                                                                                                                  |
| [#SingleInstance](https://www.autohotkey.com/docs/commands/_SingleInstance.htm)               | This directive is provided by default (SingleInstance Off for the main thread)                                   |
| [#UseHook](https://www.autohotkey.com/docs/commands/_UseHook.htm)                             |                                                                                                                  |
| [#Warn](https://www.autohotkey.com/docs/commands/_Warn.htm)                                   | Not relevant for this library                                                                                    |
| [#AllowSameLineComments](https://www.autohotkey.com/docs/commands/_AllowSameLineComments.htm) | Not relevant for this library                                                                                    |
| [#ClipboardTimeout](https://www.autohotkey.com/docs/commands/_ClipboardTimeout.htm)           | Not relevant for this library                                                                                    |
| [#CommentFlag](https://www.autohotkey.com/docs/commands/_CommentFlag.htm)                     | Not relevant for this library                                                                                    |
| [#ErrorStdOut](https://www.autohotkey.com/docs/commands/_ErrorStdOut.htm)                     | Not relevant for this library                                                                                    |
| [#EscapeChar](https://www.autohotkey.com/docs/commands/_EscapeChar.htm)                       | Not relevant for this library                                                                                    |
| [#InstallKeybdHook](https://www.autohotkey.com/docs/commands/_InstallKeybdHook.htm)           | Not relevant for this library                                                                                    |
| [#InstallMouseHook](https://www.autohotkey.com/docs/commands/_InstallMouseHook.htm)           | Not relevant for this library                                                                                    |
| [#If](https://www.autohotkey.com/docs/commands/_If.htm)                                       | Not relevant for this library                                                                                    |
| [#IfTimeout](https://www.autohotkey.com/docs/commands/_IfTimeout.htm)                         | Not relevant for this library                                                                                    |
