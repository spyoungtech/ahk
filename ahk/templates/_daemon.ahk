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
    } {% for i in range(2, 8) %} else if (command.Length() = {{ i }}) {
          Click{% for index in range(2, i+1) %}, command[{{index}}]{% endfor %}

    }{% endfor %}

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

