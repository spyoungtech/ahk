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
    if command.Length() = 1 {
          Click
    }  else if (command.Length() = 2) {
          Click, command[2]
    } else if (command.Length() = 3) {
          Click, command[2], command[3]
    } else if (command.Length() = 4) {
          Click, command[2], command[3], command[4]
    } else if (command.Length() = 5) {
          Click, command[2], command[3], command[4], command[5]
    } else if (command.Length() = 6) {
          Click, command[2], command[3], command[4], command[5], command[6]
    } else if (command.Length() = 7) {
          Click, command[2], command[3], command[4], command[5], command[6], command[7]
    }
    return

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

stdin  := FileOpen("*", "r `n")  ; Requires [v1.1.17+]

Loop {
        query := RTrim(stdin.ReadLine(), "`n")
        commandArray := StrSplit(query, ",")
        func := commandArray[1]
        response := %func%(commandArray)
        FileAppend, %response%`n, *
}
