#NoEnv

ImageSearch(ByRef command) {
    imagepath := command[8]
    x1 := command[4]
    y1 := command[5]
    x2 := command[6]
    y2 := command[7]
    if (x2 = "A_ScreenWidth") {
        x2 := A_ScreenWidth
    }
    if (y2 = "A_ScreenHeight") {
        y2 := A_ScreenHeight
    }
    ImageSearch, xpos, ypos,% x1,% y1,% x2,% y2, %imagepath%
    s .= Format("({}, {})", xpos, ypos)
    return s
}

PixelGetColor(ByRef command) {
    x := command[3]
    y := command[4]
    if (command.Length() = 4) {
    PixelGetColor,color,% x,% y
    } else {
        options := command[5]
        PixelGetColor,color,% x,% y, %options%
    }
    return color
}

PixelSearch(ByRef command) {
    x1 := command[4]
    y1 := command[5]
    x2 := command[6]
    y2 := command[7]
    if (x2 = "A_ScreenWidth") {
        x2 := A_ScreenWidth
    }
    if (y2 = "A_ScreenHeight") {
        y2 := A_ScreenHeight
    }
    if (command.Length() = 9) {
        PixelSearch, xpos, ypos,% x1,% y1,% x2,% y2, command[8], command[9]
    } else {
        options := command[10]
        PixelSearch, xpos, ypos,% x1,% y1,% x2,% y2, command[8], command[9], %options%
    }
    s .= Format("({}, {})", xpos, ypos)
    return s
}


MouseGetPos(ByRef command) {
    MouseGetPos, xpos, ypos
    s .= Format("({}, {})", xpos, ypos)
    return s
}

AHKKeyState(ByRef command) {
    if (command.Length() = 3) {
        if (GetKeyState(command[2], command[3])) {
            return 1
        } else {
            return 0
        }
    } else{
        if (GetKeyState(command[2])) {
            return 1
        } else {
            return 0
        }
    }
}

MouseMove(ByRef command) {
    if (command.Length() = 5) {
    MouseMove, command[2], command[3], command[4], R
    } else {
    MouseMove, command[2], command[3], command[4]
    }
}

CoordMode(ByRef command) {
    if (command.Length() = 2) {
        CoordMode,% command[2]
    } else {
        CoordMode,% command[2],% command[3]
    }
}


Click(ByRef command) {
    if (command.Length() = 1) {
          Click
    } {% for i in range(2, 8) %} else if (command.Length() = {{ i }}) {
          Click{% for index in range(2, i+1) %}, command[{{index}}]{% endfor %}

    }{% endfor %}

    return

}

MouseClickDrag(ByRef command) {
    button := command[2]
    if (command.Length() = 6) {
        MouseClickDrag,%button%,command[3],command[4],command[5],command[6]
    } else if (command.Length() = 7) {
        MouseClickDrag,%button%,command[3],command[4],command[5],command[6],command[7]
    } else if (command.Length() = 8) {
        MouseClickDrag,%button%,command[3],command[4],command[5],command[6],command[7],R
    }
}

RegRead(ByRef command) {
    keyname := command[3]
    RegRead, output, %keyname%, command[4]
    return output
}

SetRegView(ByRef command) {
    view := command[2]
    SetRegView, %view%
}

RegWrite(ByRef command) {
    valuetype := command[2]
    keyname := command[3]

    RegWrite, %valuetype%, %keyname%, command[4]
}

RegDelete(ByRef command) {
    keyname := command[2]
    RegDelete, %keyname%, command[3]
}

KeyWait(ByRef command) {
    keyname := command[2]
    if (command.Length() = 2) {
        KeyWait,% keyname
    } else {
        options := command[3]
        KeyWait,% keyname,% options
    }
    return ErrorLevel
}

SetKeyDelay(ByRef command) {
    SetKeyDelay, command[2], command[3]
}

Join(sep, params*) {
    for index,param in params
        str .= param . sep
    return SubStr(str, 1, -StrLen(sep))
}

Unescape(HayStack) {
    ReplacedStr := StrReplace(Haystack, "``n" , "`n")
    return ReplacedStr
}

Send(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    Send,% str
}

SendRaw(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    SendRaw,% str
}

SendInput(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    SendInput,% str
}


SendEvent(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    SendEvent,% str
}

SendPlay(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    SendPlay,% str
}

SetCapsLockState(ByRef command) {
    if (command.Length() = 1) {
        SetCapsLockState % !GetKeyState("CapsLock", "T")
    } else {
        state := command[2]
        SetCapsLockState, %state%
    }
}

HideTrayTip(ByRef command) {
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        Menu Tray, NoIcon
        Sleep 200 ; It may be necessary to adjust this sleep.
        Menu Tray, Icon
    }
}

WinGetTitle(ByRef command) {
    title := command[3]
    WinGetTitle, text, %title%
    return text
}
WinGetClass(ByRef command) {
    title := command[3]
    WinGetClass, text, %title%
    return text
}
WinGetText(ByRef command) {
    title := command[3]
    WinGetText, text, %title%
    return text
}

WinActivate(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinActivate, %title%
    } else {
        secondstowait := command[3]
        WinActivate, %title%, %secondstowait%
    }
}

WinActivateBottom(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinActivateBottom, %title%
    } else {
        secondstowait := command[3]
        WinActivateBottom, %title%, %secondstowait%
    }
}

WinClose(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinClose,% title
    } else {
        secondstowait := command[3]
        WinClose, %title%, %secondstowait%
    }
}

WinHide(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinHide, %title%
    } else {
        secondstowait := command[3]
        WinHide, %title%, %secondstowait%
    }
}

WinKill(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinKill, %title%
    } else {
        secondstowait := command[3]
        WinKill, %title%, %secondstowait%
    }
}

WinMaximize(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinMaximize, %title%
    } else {
        secondstowait := command[3]
        WinMaximize, %title%, %secondstowait%
    }
}

WinMinimize(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinMinimize, %title%
    } else {
        secondstowait := command[3]
        WinMinimize, %title%, %secondstowait%
    }
}

WinRestore(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinRestore, %title%
    } else {
        secondstowait := command[3]
        WinRestore, %title%, %secondstowait%
    }
}

WinShow(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinShow, %title%
    } else {
        secondstowait := command[3]
        WinShow, %title%, %secondstowait%
    }
}

WinWait(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinWait, %title%
    } else {
        secondstowait = command[3]
        WinWait, %title%, %secondstowait%
    }
}

WinWaitActive(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinWaitActive, %title%
    } else {
        secondstowait := command[3]
        WinWaitActive, %title%, %secondstowait%
    }
}

WinWaitNotActive(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinWaitNotActive, %title%
    } else {
        secondstowait = command[3]
        WinWaitNotActive, %title%, %secondstowait%
    }
}

WinWaitClose(ByRef command) {
    title := command[2]
    if (command.Length() = 2) {
        WinWaitClose, %title%
    } else {
        secondstowait := command[3]
        WinWaitClose, %title%, %secondstowait%
    }
}


WindowList(ByRef command) {
    WinGet windows, List
    Loop %windows%
    {
        id := windows%A_Index%
        r .= id . "`,"
    }
    return r
}

WinSend(ByRef command) {
    title := command[2]
    command.RemoveAt(1)
    command.RemoveAt(1)
    str := Join(",", command*)
    keys := Unescape(str)
    ControlSend,,% keys, %title%
}

WinSendRaw(ByRef command) {
    title := command[2]
    command.RemoveAt(1)
    command.RemoveAt(1)
    str := Join(",", command*)
    keys := Unescape(str)
    ControlSendRaw,,% keys, %title%
}

ControlSend(ByRef command) {
    ctrl := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    command.RemoveAt(1)
    command.RemoveAt(1)
    command.RemoveAt(1)
    command.RemoveAt(1)
    command.RemoveAt(1)
    command.RemoveAt(1)
    str := Join(",", command*)
    keys := Unescape(str)
    ControlSend, %ctrl%,% keys, %title%, %text%, %extitle%, %extext%
}


BaseCheck(ByRef command) {
    kommand := command[2]
    title := command[3]
    if %kommand%(title) {
        return 1
    }
    else {
        return 0
    }
}

FromMouse(ByRef command) {
    MouseGetPos,,, MouseWin
    return MouseWin
}

WinGet(ByRef command) {
    title := command[4]
    text := command[5]
    extitle := command[6]
    extext := command[7]
    WinGet, output,% command[3], %title%, %text%, %extitle%, %extext%
    return output
}

WinSet(ByRef command) {
    subcommand := command[2]
    title := command[4]
    value := command[3]

    WinSet,%subcommand%,%value%,%title%
}

WinSetTitle(ByRef command) {
    newtitle := command[4]
    WinSetTitle,% command[2],, %newtitle%
}

WinIsAlwaysOnTop(ByRef command) {
    title := command[2]
    WinGet, ExStyle, ExStyle, %title%
    if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
        return 1
    else
        return 0
}

WinClick(ByRef command) {
    x := command[2]
    y := command[3]
    hwnd := command[4]
    button := command[5]
    n := command[6]
    if (command.Length() = 6) {
        ControlClick,x%x% y%y%,%hwnd%,,%button%,%n%
    } else {
        options := command[6]
        ControlClick, x%x% y%y%, %hwnd%,,%button%, %n%, options
    }
}

AHKWinMove(ByRef command) {
    title := command [2]
    x := command[3]
    y := command[4]
    if (command.Length()) = 4 {
        WinMove,%title%,,%x%,%y%
    } else if (command.Length() = 5) {
        a := command[5]
        WinMove,%title%,,%x%,%y%,%a%
    } else if (command.Length() = 6) {
        a := command[5]
        b := command[6]
        WinMove,%title%,,%x%,%y%,%a%,%b%
    }
}

AHKWinGetPos(ByRef command) {
    title := command[2]
    WinGetPos, x, y, width, height, %title%
    if (command.Length() = 3) {
        pos_info := command[3]
        if (pos_info = "position") {
            s .= Format("({}, {})", x, y)
        } else if (pos_info = "height") {
            s .= Format("({})", height)
        } else if (pos_info = "width") {
            s .= Format("({})", width)
        }
    } else {
        s .= Format("({}, {}, {}, {})", x, y, width, height)
    }
    return s
}

CountNewlines(ByRef s) {
    newline := "`n"
    StringReplace, s, s, %newline%, %newline%, UseErrorLevel
    count := ErrorLevel
    return count
}

stdin  := FileOpen("*", "r `n")  ; Requires [v1.1.17+]

Loop {
        query := RTrim(stdin.ReadLine(), "`n")
        commandArray := StrSplit(query, ",")
        func := commandArray[1]
        response := %func%(commandArray)
        newline_count := CountNewlines(response)
        FileAppend, %newline_count%`n, *
        FileAppend, %response%`n, *
}

