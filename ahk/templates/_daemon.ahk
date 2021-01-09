#SingleInstance Force
#NoEnv



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
    if (command.Length() = 6 {
        MouseclickDrag,command[2],command[3],command[4],command[5],command[6]
    } else if (command.Length() = 7 {
        MouseclickDrag,command[2],command[3],command[4],command[5],command[6],command[7]
    } else if (command.Length() = 8 {
        MouseclickDrag,command[2],command[3],command[4],command[5],command[6],command[7],command[8]
    }
}

RegRead(ByRef command) {
    RegRead, output, command[3], command[4]
    return %output%
}

SetRegView(ByRef command) {
    SetRegView, command[2]
}

RegWrite(ByRef command) {
    RegWrite, command[2], command[3], command[4]
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

