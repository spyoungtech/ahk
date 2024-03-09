.. role:: raw-html-m2r(raw)
   :format: html


Available Methods
=================


Most methods from autohotkey are implemented in this wrapper. This page can serve as a quick reference to find
Python equivalents of AutoHotkey commands/functions that are implemented in the wrapper.

Methods that are not implemented are also noted here for reference. This is a work in progress and may not list all [un]available methods.
Check the full API reference for more complete information.

Mouse and Keyboard
^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `#KeyHistory <https://www.autohotkey.com/docs/commands/_KeyHistory.htm>`_
     - Not Implemented
     -
   * - `BlockInput <https://www.autohotkey.com/docs/commands/BlockInput.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.block_input`
   * - `Click <https://www.autohotkey.com/docs/commands/Click.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.click`
   * - `Send <https://www.autohotkey.com/docs/v1/lib/Send.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.send` / :py:meth:`~ahk._sync.engine.AHK.send_raw` / :py:meth:`~ahk._sync.engine.AHK.send_input`
   * - `ControlClick <https://www.autohotkey.com/docs/commands/ControlClick.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.control_click` / :py:meth:`~ahk._sync.window.Window.click` (:py:class:`~ahk._sync.window.Window` method)
   * - `ControlSend[Raw] <https://www.autohotkey.com/docs/commands/ControlSend.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.control_send` / :py:meth:`~ahk._sync.engine.AHK.Control.send`
   * - `CoordMode <https://www.autohotkey.com/docs/commands/CoordMode.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.set_coord_mode` (or as a parameter to methods affected by the coord mode)
   * - `GetKeyName() <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
     - Not Implemented
     -
   * - `GetKeySC() <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
     - Not Implemented
     -
   * - `GetKeyState <https://www.autohotkey.com/docs/commands/GetKeyState.htm#command>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.key_state`
   * - `GetKeyVK() <https://www.autohotkey.com/docs/commands/GetKey.htm>`_
     - Not Implemented
     -
   * - `KeyHistory <https://www.autohotkey.com/docs/commands/KeyHistory.htm>`_
     - Not Implemented
     -
   * - `KeyWait <https://www.autohotkey.com/docs/commands/KeyWait.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.key_wait`
   * - `Input <https://www.autohotkey.com/docs/commands/Input.htm>`_
     - Not Implemented
     - Use python ``input()`` instead
   * - `InputHook() <https://www.autohotkey.com/docs/commands/InputHook.htm>`_
     - Not Implemented
     -
   * - `MouseClick <https://www.autohotkey.com/docs/commands/MouseClick.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.click`
   * - `MouseClickDrag <https://www.autohotkey.com/docs/commands/MouseClickDrag.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.mouse_drag`
   * - `MouseGetPos <https://www.autohotkey.com/docs/commands/MouseGetPos.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.get_mouse_position` / :py:attr:`~ahk._sync.engine.AHK.mouse_position`
   * - `MouseMove <https://www.autohotkey.com/docs/commands/MouseMove.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.mouse_move`
   * - `SendLevel <https://www.autohotkey.com/docs/commands/SendLevel.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.set_send_level`
   * - `SendMode <https://www.autohotkey.com/docs/commands/SendMode.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.set_send_mode`
   * - `SetCapsLockState <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.set_capslock_state`
   * - `SetDefaultMouseSpeed <https://www.autohotkey.com/docs/commands/SetDefaultMouseSpeed.htm>`_
     - Implemented
     - Speed is controlled by the ``speed`` keyword argument of relevant methods (for example, see :py:meth:`~ahk._sync.engine.AHK.mouse_move`)
   * - `SetKeyDelay <https://www.autohotkey.com/docs/commands/SetKeyDelay.htm>`_
     - Implemented
     - Delay is controlled by the ``delay`` keyword argument of relevant methods
   * - `SetMouseDelay <https://www.autohotkey.com/docs/commands/SetMouseDelay.htm>`_
     - Not Implemented
     - Delays between mouse movements can be controlled in Python code between calls to ``mouse_move``
   * - `SetNumLockState <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_
     - Not Implemented
     -
   * - `SetScrollLockState <https://www.autohotkey.com/docs/commands/SetNumScrollCapsLockState.htm>`_
     - Not Implemented
     -
   * - `SetStoreCapsLockMode <https://www.autohotkey.com/docs/commands/SetStoreCapslockMode.htm>`_
     - Not Implemented
     -


Hotkeys
^^^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `Hotkeys <https://www.autohotkey.com/docs/Hotkeys.htm>`_
     - Implemented
     - Before 1.0, callbacks were only supported as Autohotkey Scripts\ :raw-html-m2r:`<br/>` In 1.0 and later, callbacks are supported as Python functions
   * - `Hotstrings <https://www.autohotkey.com/docs/Hotstrings.htm>`_
     - Implemented
     - Available in 1.0+
   * - `Suspend <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
     - Implemented*
     - Use stop_hotkeys and start_hotkeys to enable/disable hotkeys


ClipBoard
^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `OnClipboardChange() <https://www.autohotkey.com/docs/commands/OnClipboardChange.htm#function>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.on_clipboard_change`
   * - `Clipboard/ClipboardAll <https://www.autohotkey.com/docs/misc/Clipboard.htm#ClipboardAll>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.get_clipboard` / :py:meth:`~ahk._sync.engine.AHK.set_clipboard` / :py:meth:`~ahk._sync.engine.AHK.get_clipboard_all` / :py:meth:`~ahk._sync.engine.AHK.set_clipboard_all`
   * - `ClipWait <https://www.autohotkey.com/docs/v1/lib/ClipWait.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.clip_wait`


Screen/Image
^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `ImageSearch <https://www.autohotkey.com/docs/commands/ImageSearch.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.image_search`
   * - `PixelGetColor <https://www.autohotkey.com/docs/commands/PixelGetColor.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.pixel_get_color`
   * - `PixelSearch <https://www.autohotkey.com/docs/commands/PixelSearch.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.pixel_search`


Registry
^^^^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `RegDelete <https://www.autohotkey.com/docs/commands/RegDelete.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.reg_delete`
   * - `RegRead <https://www.autohotkey.com/docs/commands/RegRead.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.reg_read`
   * - `RegWrite <https://www.autohotkey.com/docs/commands/RegWrite.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.reg_write`
   * - `SetRegView <https://www.autohotkey.com/docs/commands/SetRegView.htm>`_
     - Not Implemented
     -


Window
^^^^^^

Window | Controls
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `Control <https://www.autohotkey.com/docs/commands/Control.htm>`_
     - Implemented
     -
   * - `ControlClick <https://www.autohotkey.com/docs/commands/ControlClick.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.window.Window.click` (uses :py:meth:`~ahk._sync.engine.AHK.control_click`)
   * - `ControlFocus <https://www.autohotkey.com/docs/commands/ControlFocus.htm>`_
     - Not Implemented
     -
   * - `ControlGet <https://www.autohotkey.com/docs/commands/ControlGet.htm>`_
     - Implemented
     -
   * - `ControlGetFocus <https://www.autohotkey.com/docs/commands/ControlGetFocus.htm>`_
     - Not Implemented
     -
   * - `ControlGetPos <https://www.autohotkey.com/docs/commands/ControlGetPos.htm>`_
     - Implemented
     -
   * - `ControlGetText <https://www.autohotkey.com/docs/commands/ControlGetText.htm>`_
     - Implemented
     -
   * - `ControlMove <https://www.autohotkey.com/docs/commands/ControlMove.htm>`_
     - Implemented
     -
   * - `ControlSend[Raw] <https://www.autohotkey.com/docs/commands/ControlSend.htm>`_
     - Implemented
     -
   * - `ControlSetText <https://www.autohotkey.com/docs/commands/ControlSetText.htm>`_
     - Implemented
     -
   * - `Menu <https://www.autohotkey.com/docs/commands/Menu.htm>`_
     - Not Implemented
     -
   * - `PostMessage/SendMessage <https://www.autohotkey.com/docs/commands/PostMessage.htm>`_
     - Not Implemented
     -
   * - `SetControlDelay <https://www.autohotkey.com/docs/commands/SetControlDelay.htm>`_
     - Not Implemented
     -
   * - `WinMenuSelectItem <https://www.autohotkey.com/docs/commands/WinMenuSelectItem.htm>`_
     - Not Implemented
     -


Window | Groups
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `GroupActivate <https://www.autohotkey.com/docs/commands/GroupActivate.htm>`_
     -
     -
   * - `GroupAdd <https://www.autohotkey.com/docs/commands/GroupAdd.htm>`_
     -
     -
   * - `GroupClose <https://www.autohotkey.com/docs/commands/GroupClose.htm>`_
     -
     -
   * - `GroupDeactivate <https://www.autohotkey.com/docs/commands/GroupDeactivate.htm>`_
     -
     -


Window functions
^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `#WinActivateForce <https://www.autohotkey.com/docs/commands/_WinActivateForce.htm>`_
     - Implemented
     - Any directive can be added to the daemon
   * - `DetectHiddenText <https://www.autohotkey.com/docs/commands/DetectHiddenText.htm>`_
     - Planned
     -
   * - `DetectHiddenWindows <https://www.autohotkey.com/docs/commands/DetectHiddenWindows.htm>`_
     - Implemented
     - Use ``detect_hidden_windows`` parameter of relevant functions or :py:meth:`~ahk._sync.engine.AHK.set_detect_hidden_windows`
   * - `IfWin[Not]Active <https://www.autohotkey.com/docs/commands/IfWinActive.htm>`_
     - Not Implemented
     - Use Python ``if`` with ``win_active``\ /\ ``win.is_active``
   * - `IfWin[Not]Exist <https://www.autohotkey.com/docs/commands/IfWinExist.htm>`_
     - Not Implemented
     - Use Python ``if`` with ``win_exists``\ /\ ``win.exists``
   * - `SetTitleMatchMode <https://www.autohotkey.com/docs/commands/SetTitleMatchMode.htm>`_
     - Implemented
     -
   * - `SetWinDelay <https://www.autohotkey.com/docs/commands/SetWinDelay.htm>`_
     - Not Implemented
     - Delays can be controlled in Python code
   * - `StatusBarGetText <https://www.autohotkey.com/docs/commands/StatusBarGetText.htm>`_
     - Not Implemented
     -
   * - `StatusBarWait <https://www.autohotkey.com/docs/commands/StatusBarWait.htm>`_
     - Not Implemented
     -
   * - `WinActivate <https://www.autohotkey.com/docs/commands/WinActivate.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_activate`  / :py:meth:`~ahk._sync.window.Window.activate` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinActivateBottom <https://www.autohotkey.com/docs/commands/WinActivateBottom.htm>`_
     - Implemented
     -
   * - `WinActive() <https://www.autohotkey.com/docs/commands/WinActive.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.window.Window.activate` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinClose <https://www.autohotkey.com/docs/commands/WinClose.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_close` / :py:meth:`~ahk._sync.window.Window.close` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinExist() <https://www.autohotkey.com/docs/commands/WinExist.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_exist` / :py:meth:`~ahk._sync.window.Window.exists` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinGet <https://www.autohotkey.com/docs/commands/WinGet.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_get` See also :py:meth:`~ahk._sync.engine.AHK.find_windows` and variants.
   * - `WinGetActiveStats <https://www.autohotkey.com/docs/commands/WinGetActiveStats.htm>`_
     - Not Implemented
     -
   * - `WinGetActiveTitle <https://www.autohotkey.com/docs/commands/WinGetActiveTitle.htm>`_
     - Not Implemented
     - Use :py:meth:`~ahk._sync.engine.AHK.get_active_window` and :py:attr:`~ahk._sync.window.Window.title` property
   * - `WinGetClass <https://www.autohotkey.com/docs/commands/WinGetClass.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_get_class` / :py:meth:`~ahk._sync.window.Window.get_class` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinGetPos <https://www.autohotkey.com/docs/commands/WinGetPos.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_get_position` / :py:meth:`~ahk._sync.window.Window.get_position` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinGetText <https://www.autohotkey.com/docs/commands/WinGetText.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_get_text` / :py:meth:`~ahk._sync.window.Window.get_text` (:py:class:`~ahk._sync.window.Window` method)
   * - `WinGetTitle <https://www.autohotkey.com/docs/commands/WinGetTitle.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_get_title` / :py:meth:`~ahk._sync.window.Window.get_title` or :py:attr:`~ahk._sync.window.Window.title` (:py:class:`~ahk._sync.window.Window`)
   * - `WinHide <https://www.autohotkey.com/docs/commands/WinHide.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_hide` / :py:meth:`~ahk._sync.window.Window.hide` (:py:class:`~ahk._sync.window.Window`)
   * - `WinKill <https://www.autohotkey.com/docs/commands/WinKill.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_kill` / :py:meth:`~ahk._sync.window.Window.kill` (:py:class:`~ahk._sync.window.Window`)
   * - `WinMaximize <https://www.autohotkey.com/docs/commands/WinMaximize.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_maximize` / :py:meth:`~ahk._sync.window.Window.maximize` (:py:class:`~ahk._sync.window.Window`)
   * - `WinMinimize <https://www.autohotkey.com/docs/commands/WinMinimize.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_minimize` / :py:meth:`~ahk._sync.window.Window.minimize` (:py:class:`~ahk._sync.window.Window`)
   * - `WinMinimizeAll[Undo] <https://www.autohotkey.com/docs/commands/WinMinimizeAll.htm>`_
     - Not Implemented
     -
   * - `WinMove <https://www.autohotkey.com/docs/commands/WinMove.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_move`
   * - `WinRestore <https://www.autohotkey.com/docs/commands/WinRestore.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_restore`
   * - `WinSet <https://www.autohotkey.com/docs/commands/WinSet.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_set_always_on_top` / :py:meth:`~ahk._sync.engine.AHK.win_set_bottom` / :py:meth:`~ahk._sync.engine.AHK.win_set_disable` / :py:meth:`~ahk._sync.engine.AHK.win_set_enable` / :py:meth:`~ahk._sync.engine.AHK.win_set_ex_style` / :py:meth:`~ahk._sync.engine.AHK.win_set_redraw` / :py:meth:`~ahk._sync.engine.AHK.win_set_region` / :py:meth:`~ahk._sync.engine.AHK.win_set_style` / :py:meth:`~ahk._sync.engine.AHK.win_set_title` / :py:meth:`~ahk._sync.engine.AHK.win_set_top` / :py:meth:`~ahk._sync.engine.AHK.win_set_trans_color` / :py:meth:`~ahk._sync.engine.AHK.win_set_transparent`

   * - `WinSetTitle <https://www.autohotkey.com/docs/commands/WinSetTitle.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_set_title`
   * - `WinShow <https://www.autohotkey.com/docs/commands/WinShow.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_show`
   * - `WinWait <https://www.autohotkey.com/docs/commands/WinWait.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_wait`
   * - `WinWait[Not]Active <https://www.autohotkey.com/docs/commands/WinWaitActive.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_wait_not_active`
   * - `WinWaitClose <https://www.autohotkey.com/docs/commands/WinWaitClose.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.win_wait_close`


Sound
^^^^^

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `SoundBeep <https://www.autohotkey.com/docs/commands/SoundBeep.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.sound_beep`
   * - `SoundGet <https://www.autohotkey.com/docs/commands/SoundGet.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.sound_get`
   * - `SoundGetWaveVolume <https://www.autohotkey.com/docs/commands/SoundGetWaveVolume.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.get_volume`
   * - `SoundPlay <https://www.autohotkey.com/docs/commands/SoundPlay.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.sound_play`
   * - `SoundSet <https://www.autohotkey.com/docs/commands/SoundSet.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.sound_set`
   * - `SoundSetWaveVolume <https://www.autohotkey.com/docs/commands/SoundSetWaveVolume.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.set_volume`


GUI
^^^

GUI methods are largely unimplmented, except ``ToolTip`` and ``TrayTip``.
We recommend using one of the many `Python GUI libraries <https://wiki.python.org/moin/GuiProgramming>`_, such as ``tkinter`` from the standard library or a third
party package such as `pyqt <https://wiki.python.org/moin/PyQt>`_ , `pysimplegui <https://www.pysimplegui.org/en/latest/>`_ or similar.

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Status
     - Notes
   * - `Gui <https://www.autohotkey.com/docs/commands/Gui.htm>`_
     - Not Implemented
     -
   * - `Gui control types <https://www.autohotkey.com/docs/commands/GuiControls.htm>`_
     - Not Implemented
     -
   * - `GuiControl <https://www.autohotkey.com/docs/commands/GuiControl.htm>`_
     - Not Implemented
     -
   * - `GuiControlGet <https://www.autohotkey.com/docs/commands/GuiControlGet.htm>`_
     - Not Implemented
     -
   * - `Gui ListView control <https://www.autohotkey.com/docs/commands/ListView.htm>`_
     - Not Implemented
     -
   * - `Gui TreeView control <https://www.autohotkey.com/docs/commands/TreeView.htm>`_
     - Not planned
     -
   * - `IfMsgBox <https://www.autohotkey.com/docs/commands/IfMsgBox.htm>`_
     - Not planned
     -
   * - `InputBox <https://www.autohotkey.com/docs/commands/InputBox.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.input_box`
   * - `FileSelectFile <https://www.autohotkey.com/docs/commands/FileSelectFile.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.file_select_box`
   * - `FileSelectFolder <https://www.autohotkey.com/docs/commands/FileSelectFile.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.folder_select_box`
   * - `LoadPicture() <https://www.autohotkey.com/docs/commands/LoadPicture.htm>`_
     - Not Implemented
     -
   * - `Menu <https://www.autohotkey.com/docs/commands/Menu.htm>`_
     - Not Implemented
     -
   * - `MenuGetHandle() <https://www.autohotkey.com/docs/commands/MenuGetHandle.htm>`_
     - Not Planned
     -
   * - `MenuGetName() <https://www.autohotkey.com/docs/commands/MenuGetName.htm>`_
     - Not Planned
     -
   * - `MsgBox <https://www.autohotkey.com/docs/commands/MsgBox.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.msg_box`
   * - `OnMessage() <https://www.autohotkey.com/docs/commands/OnMessage.htm>`_
     - Not Planned
     -
   * - `Progress <https://www.autohotkey.com/docs/commands/Progress.htm>`_
     - Not Planned
     -
   * - `SplashImage <https://www.autohotkey.com/docs/commands/Progress.htm>`_
     - Not Planned
     -
   * - `SplashTextOn/Off <https://www.autohotkey.com/docs/commands/SplashTextOn.htm>`_
     - Not Planned
     -
   * - `ToolTip <https://www.autohotkey.com/docs/commands/ToolTip.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.show_tooltip`
   * - `TrayTip <https://www.autohotkey.com/docs/commands/TrayTip.htm>`_
     - Implemented
     - :py:meth:`~ahk._sync.engine.AHK.show_traytip`


Directives
^^^^^^^^^^

In general, all directives are technically usable, however many do not have applicable context in the Python library.

Directives are mentioned in tables above and are omitted from this table.


For example, to use the :py:class:`~ahk.directives.NoTrayIcon` directive

    from ahk import AHK
    from ahk.directives import NoTrayIcon
    ahk = AHK(directives=[NoTrayIcon])

.. list-table::
   :header-rows: 1

   * - AutoHotkey Command
     - Notes
   * - `#HotkeyInterval <https://www.autohotkey.com/docs/commands/_HotkeyInterval.htm>`_
     -
   * - `#HotkeyModifierTimeout <https://www.autohotkey.com/docs/commands/_HotkeyModifierTimeout.htm>`_
     -
   * - `#Hotstring <https://www.autohotkey.com/docs/commands/_Hotstring.htm>`_
     -
   * - `#Include[Again] <https://www.autohotkey.com/docs/commands/_Include.htm>`_
     - Using this directive is strongly discouraged as it is **very** likely to cause issues. Use with extreme caution.
   * - `#InputLevel <https://www.autohotkey.com/docs/commands/_InputLevel.htm>`_
     -
   * - `#KeyHistory <https://www.autohotkey.com/docs/commands/_KeyHistory.htm>`_
     -
   * - `#MaxHotkeysPerInterval <https://www.autohotkey.com/docs/commands/_MaxHotkeysPerInterval.htm>`_
     -
   * - `#MaxMem <https://www.autohotkey.com/docs/commands/_MaxMem.htm>`_
     -
   * - `#MaxThreads <https://www.autohotkey.com/docs/commands/_MaxThreads.htm>`_
     -
   * - `#MaxThreadsBuffer <https://www.autohotkey.com/docs/commands/_MaxThreadsBuffer.htm>`_
     -
   * - `#MaxThreadsPerHotkey <https://www.autohotkey.com/docs/commands/_MaxThreadsPerHotkey.htm>`_
     - Hotkey callbacks are run in Python, so this largely won't have any significant effect
   * - `#MenuMaskKey <https://www.autohotkey.com/docs/commands/_MenuMaskKey.htm>`_
     -
   * - `#NoEnv <https://www.autohotkey.com/docs/commands/_NoEnv.htm>`_
     - Removed in ``ahk`` v1.0.0 -- Used by default when using AutoHotkey v1. Not available in AutoHotkey v2.
   * - `#NoTrayIcon <https://www.autohotkey.com/docs/commands/_NoTrayIcon.htm>`_
     - If you use hotkeys or hotstrings, you probably also want to configure this as a hotkey transport option
   * - `#Persistent <https://www.autohotkey.com/docs/commands/_Persistent.htm>`_
     - This is on by default in scripts run by this library
   * - `#Requires <https://www.autohotkey.com/docs/commands/_Requires.htm>`_
     -
   * - `#SingleInstance <https://www.autohotkey.com/docs/commands/_SingleInstance.htm>`_
     - This directive is provided by default (SingleInstance Off for the main thread)
   * - `#UseHook <https://www.autohotkey.com/docs/commands/_UseHook.htm>`_
     -
   * - `#Warn <https://www.autohotkey.com/docs/commands/_Warn.htm>`_
     - Not relevant for this library
   * - `#AllowSameLineComments <https://www.autohotkey.com/docs/commands/_AllowSameLineComments.htm>`_
     - Not relevant for this library
   * - `#ClipboardTimeout <https://www.autohotkey.com/docs/commands/_ClipboardTimeout.htm>`_
     - Not relevant for this library
   * - `#CommentFlag <https://www.autohotkey.com/docs/commands/_CommentFlag.htm>`_
     - Not relevant for this library
   * - `#ErrorStdOut <https://www.autohotkey.com/docs/commands/_ErrorStdOut.htm>`_
     - Not relevant for this library
   * - `#EscapeChar <https://www.autohotkey.com/docs/commands/_EscapeChar.htm>`_
     - Not relevant for this library
   * - `#InstallKeybdHook <https://www.autohotkey.com/docs/commands/_InstallKeybdHook.htm>`_
     - Not relevant for this library
   * - `#InstallMouseHook <https://www.autohotkey.com/docs/commands/_InstallMouseHook.htm>`_
     - Not relevant for this library
   * - `#If <https://www.autohotkey.com/docs/commands/_If.htm>`_
     - Not relevant for this library
   * - `#IfTimeout <https://www.autohotkey.com/docs/commands/_IfTimeout.htm>`_
     - Not relevant for this library
