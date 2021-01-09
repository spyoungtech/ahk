#SingleInstance Force
#NoEnv

ImageSearch(ByRef command) {
    imagepath := command[8]
    ImageSearch, xpos, ypos, command[4], command[5], command[6], command[7], %imagepath%
    s .= Format("({}, {})", xpos, ypos)
    return s
}

PixelGetColor(ByRef command) {
    if (command.Length() = 4) {
    PixelGetColor,color,command[3],command[4]
    } else {
        options := command[5]
        PixelGetColor,color,command[3],command[4], %options%
    }
    return color
}

PixelSearch(ByRef command) {
    if (command.Length() = 9) {
        PixelSearch, xpos, ypos, command[4], command[5], command[6], command[7], command[8], command[9]
    } else {
        options := command[10]
        PixelSearch, xpos, ypos, command[4], command[5], command[6], command[7], command[8], command[9], %options%
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
        CoordMode, command[2]
    } else {
        CoordMode, command[2], command[3]
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
    SetKeyDelay, command[2]
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

stdin  := FileOpen("*", "r `n")  ; Requires [v1.1.17+]

Loop {
        query := RTrim(stdin.ReadLine(), "`n")
        commandArray := StrSplit(query, ",")
        func := commandArray[1]
        response := %func%(commandArray)
        FileAppend, %response%`n, *
}

