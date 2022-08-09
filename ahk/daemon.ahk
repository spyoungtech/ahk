#NoEnv
#Persistent
#SingleInstance Off

RESPONSEMESSAGE := "000" ; ResponseMessage
TUPLERESPONSEMESSAGE := "001" ; TupleResponseMessage
COORDINATERESPONSEMESSAGE := "002" ; CoordinateResponseMessage
INTEGERRESPONSEMESSAGE := "003" ; IntegerResponseMessage
BOOLEANRESPONSEMESSAGE := "004" ; BooleanResponseMessage
STRINGRESPONSEMESSAGE := "005" ; StringResponseMessage
WINDOWIDLISTRESPONSEMESSAGE := "006" ; WindowIDListResponseMessage
NOVALUERESPONSEMESSAGE := "007" ; NoValueResponseMessage
EXCEPTIONRESPONSEMESSAGE := "008" ; ExceptionResponseMessage
WINDOWCONTROLLISTRESPONSEMESSAGE := "009" ; WindowControlListResponseMessage
WINDOWRESPONSEMESSAGE := "00a" ; WindowResponseMessage
NOVALUE_SENTINEL := Chr(57344)

FormatResponse(MessageType, payload) {
    newline_count := CountNewlines(payload)
    response := Format("{}`n{}`n{}`n", MessageType, newline_count, payload)
    return response
}

FormatNoValueResponse() {
    global NOVALUE_SENTINEL
    global NOVALUERESPONSEMESSAGE
    return FormatResponse(NOVALUERESPONSEMESSAGE, NOVALUE_SENTINEL)
}

AHKSetDetectHiddenWindows(ByRef command) {
    value := command[2]
    DetectHiddenWindows, %value%
    return FormatNoValueResponse()
}

AHKSetTitleMatchMode(ByRef command) {
    val1 := command[2]
    val2 := command[3]
    if (val1 != "") {
        SetTitleMatchMode, %val1%
    }
    if (val2 != "") {
        SetTitleMatchMode, %val2%
    }
    return FormatNoValueResponse()
}

AHKGetTitleMatchMode(ByRef command) {
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, A_TitleMatchMode)
}

AHKGetTitleMatchSpeed(ByRef command) {
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, A_TitleMatchModeSpeed)
}

AHKWinExist(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    if WinExist(title, text, extitle, extext) {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    } else {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    }
    return resp
}

AHKWinClose(ByRef command) {
    title := command[2]
    text := command[3]
    secondstowait := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinClose, %title%, %text%, %secondstowait%, %extitle%, %extext%
    return FormatNoValueResponse()
}

AHKWinGetID(ByRef command) {
    global WINDOWRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, ID, %title%, %text%, %extitle%, %extext%
    if (output = 0 || output = "") {
        response := FormatNoValueResponse()
    } else {
        response := FormatResponse(WINDOWRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}

AHKWinGetTitle(ByRef command) {
    global STRINGRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGetTitle, text, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatResponse(STRINGRESPONSEMESSAGE, text)
}

AHKWinGetIDLast(ByRef command) {
    global WINDOWRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, IDLast, %title%, %text%, %extitle%, %extext%
    if (output = 0 || output = "") {
        response := FormatNoValueResponse()
    } else {
        response := FormatResponse(WINDOWRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}


AHKWinGetPID(ByRef command) {
    global INTEGERRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
if (match_mode != "") {
    SetTitleMatchMode, %match_mode%
}
if (match_speed != "") {
    SetTitleMatchMode, %match_speed%
}

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, PID, %title%, %text%, %extitle%, %extext%
    if (output = 0 || output = "") {
        response := FormatNoValueResponse()
    } else {
        response := FormatResponse(INTEGERRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}


AHKWinGetProcessName(ByRef command) {
    global STRINGRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
if (match_mode != "") {
    SetTitleMatchMode, %match_mode%
}
if (match_speed != "") {
    SetTitleMatchMode, %match_speed%
}

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, ProcessName, %title%, %text%, %extitle%, %extext%
    if (output = 0 || output = "") {
        response := FormatNoValueResponse()
    } else {
        response := FormatResponse(STRINGRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}

AHKWinGetProcessPath(ByRef command) {
    global STRINGRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, ProcessPath, %title%, %text%, %extitle%, %extext%
    if (output = 0 || output = "") {
        response := FormatNoValueResponse()
    } else {
        response := FormatResponse(STRINGRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}


AHKWinGetCount(ByRef command) {
    global INTEGERRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, Count, %title%, %text%, %extitle%, %extext%
    if (output = 0) {
        response := FormatResponse(INTEGERRESPONSEMESSAGE, output)
    } else {
        response := FormatResponse(INTEGERRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}



AHKWinGetMinMax(ByRef command) {
    global INTEGERRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, MinMax, %title%, %text%, %extitle%, %extext%
    if (output = "") {
        response := FormatNoValueResponse()
    } else {
        response := FormatResponse(INTEGERRESPONSEMESSAGE, output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}

AHKWinGetControlList(ByRef command) {
    global EXCEPTIONRESPONSEMESSAGE
    global WINDOWCONTROLLISTRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinGet, ahkid, ID, %title%, %text%, %extitle%, %extext%

    if (ahkid = "") {
        return FormatNoValueResponse()
    }

    WinGet, ctrList, ControlList, %title%, %text%, %extitle%, %extext%
    WinGet, ctrListID, ControlListHWND, %title%, %text%, %extitle%, %extext%

    if (ctrListID = "") {
        return FormatResponse(WINDOWCONTROLLISTRESPONSEMESSAGE, Format("('{}', [])", ahkid))
    }

    ctrListArr := StrSplit(ctrList, "`n")
    ctrListIDArr := StrSplit(ctrListID, "`n")
    if (ctrListArr.Length() != ctrListIDArr.Length()) {
        return FormatResponse(EXCEPTIONRESPONSEMESSAGE, "Control hwnd/class lists have unexpected lengths")
    }

    output := Format("('{}', [", ahkid)

    for index, hwnd in ctrListIDArr {
        classname := ctrListArr[index]
        output .= Format("('{}', '{}'), ", hwnd, classname)

    }
    output .= "])"
    response := FormatResponse(WINDOWCONTROLLISTRESPONSEMESSAGE, output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}

AHKWinGetTransparent(ByRef command) {
    global INTEGERRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, Transparent, %title%, %text%, %extitle%, %extext%
    response := FormatResponse(INTEGERRESPONSEMESSAGE, output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}
AHKWinGetTransColor(ByRef command) {
    global STRINGRESPONSEMESSAGE
    global INTEGERRESPONSEMESSAGE
    global NOVALUERESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, TransColor, %title%, %text%, %extitle%, %extext%
    response := FormatResponse(NOVALUERESPONSEMESSAGE, output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}
AHKWinGetStyle(ByRef command) {
    global STRINGRESPONSEMESSAGE
    global INTEGERRESPONSEMESSAGE
    global NOVALUERESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, Style, %title%, %text%, %extitle%, %extext%
    response := FormatResponse(NOVALUERESPONSEMESSAGE, output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}
AHKWinGetExStyle(ByRef command) {
    global STRINGRESPONSEMESSAGE
    global INTEGERRESPONSEMESSAGE
    global NOVALUERESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet, output, ExStyle, %title%, %text%, %extitle%, %extext%
    response := FormatResponse(NOVALUERESPONSEMESSAGE, output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}

AHKWinGetText(ByRef command) {
    global STRINGRESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinGetText, output,%title%,%text%,%extitle%,%extext%

    if (ErrorLevel = 1) {
        return FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was an error getting window text")
    }

    response := FormatResponse(STRINGRESPONSEMESSAGE, output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
}



AHKWinSetTitle(ByRef command) {
    new_title := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }
    WinSetTitle, %title%, %text%, %new_title%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetAlwaysOnTop(ByRef command) {
    toggle := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinSet, AlwaysOntop, %toggle%, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetBottom(ByRef command) {
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinSet, Bottom,, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetTop(ByRef command) {
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinSet, Top,, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetEnable(ByRef command) {
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinSet, Enable,, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetDisable(ByRef command) {
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinSet, Disable,, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetRedraw(ByRef command) {
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }

    WinSet, Redraw,, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetStyle(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    style := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinSet, Style, %style%, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    if (ErrorLevel = 1) {
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    } else {
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    }
}

AHKWinSetExStyle(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    style := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinSet, ExStyle, %style%, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    if (ErrorLevel = 1) {
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    } else {
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    }
}

AHKWinSetRegion(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    options := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinSet, Region, %options%, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    if (ErrorLevel = 1) {
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    } else {
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    }
}

AHKWinSetTransparent(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    transparency := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinSet, Transparent, %transparency%, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}

AHKWinSetTransColor(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    color := command[2]
    title := command[3]
    text := command[4]
    extitle := command[5]
    extext := command[6]
    detect_hw := command[7]
    match_mode := command[8]
    match_speed := command[9]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }


    WinSet, TransColor, %color%, %title%, %text%, %extitle%, %extext%
    return FormatNoValueResponse()
}

ImageSearch(ByRef command) {
    global COORDINATERESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    imagepath := command[6]
    x1 := command[2]
    y1 := command[3]
    x2 := command[4]
    y2 := command[5]

    if (x2 = "A_ScreenWidth") {
        x2 := A_ScreenWidth
    }
    if (y2 = "A_ScreenHeight") {
        y2 := A_ScreenHeight
    }
    ImageSearch, xpos, ypos,% x1,% y1,% x2,% y2, %imagepath%
    if (ErrorLevel = 2) {
        s := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "there was a problem that prevented the command from conducting the search (such as failure to open the image file or a badly formatted option)")
    } else if (ErrorLevel = 1) {
        s := FormatNoValueResponse()
    } else {
        s := FormatResponse(COORDINATERESPONSEMESSAGE, Format("({}, {})", xpos, ypos))
    }

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
    s := Format("({}, {})", xpos, ypos)
    return s
}


MouseGetPos(ByRef command) {
    global COORDINATERESPONSEMESSAGE
    MouseGetPos, xpos, ypos
    payload := Format("({}, {})", xpos, ypos)
    resp := FormatResponse(COORDINATERESPONSEMESSAGE, payload)
    return resp
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
    x := command[2]
    y := command[3]
    speed := command[4]
    relative := command[5]
    if (relative != "") {
    MouseMove, %x%, %y%, %speed%, R
    } else {
    MouseMove, %x%, %y%, %speed%
    }
    resp := FormatNoValueResponse()
    return resp
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
    global INTEGERRESPONSEMESSAGE
    keyname := command[2]
    if (command.Length() = 2) {
        KeyWait,% keyname
    } else {
        options := command[3]
        KeyWait,% keyname,% options
    }
    return FormatResponse(INTEGERRESPONSEMESSAGE, ErrorLevel)
}

SetKeyDelay(ByRef command) {
    SetKeyDelay, command[2], command[3]
}

Join(sep, params*) {
    for index,param in params
        str := param . sep
    return SubStr(str, 1, -StrLen(sep))
}

Unescape(HayStack) {
    ReplacedStr := StrReplace(Haystack, "``n" , "`n")
    return ReplacedStr
}

AHKSend(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    Send,% str
    return FormatNoValueResponse()
}

AHKSendRaw(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*) ; TODO: remove after better input handling is implemented
    str := Unescape(s)
    SendRaw,% str
    return FormatNoValueResponse()
}

AHKSendInput(ByRef command) {

    str := command[2]
    SendInput,% str
    return FormatNoValueResponse()
}


SendEvent(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    SendEvent,% str
    return FormatNoValueResponse()
}

SendPlay(ByRef command) {
    command.RemoveAt(1)
    s := Join(",", command*)
    str := Unescape(s)
    SendPlay,% str
    return FormatNoValueResponse()
}

SetCapsLockState(ByRef command) {
    if (command.Length() = 1) {
        SetCapsLockState % !GetKeyState("CapsLock", "T")
    } else {
        state := command[2]
        SetCapsLockState, %state%
    }
    return FormatNoValueResponse()
}

HideTrayTip(ByRef command) {
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        Menu Tray, NoIcon
        Sleep 200 ; It may be necessary to adjust this sleep.
        Menu Tray, Icon
    }
}




WinGetClass(ByRef command) {
    title := command[3]
    WinGetClass, text, %title%
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
    global WINDOWIDLISTRESPONSEMESSAGE

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    detect_hw := command[2]
    match_mode := command[3]
    match_speed := command[4]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    if (detect_hw) {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet windows, List
    r := ""
    Loop %windows%
    {
        id := windows%A_Index%
        r .= id . "`,"
    }
    resp := FormatResponse(WINDOWIDLISTRESPONSEMESSAGE, r)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
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

AHKControlSend(ByRef command) {
    ctrl := command[2]
    keys := command[3]
    title := command[4]
    text := command[5]
    extitle := command[6]
    extext := command[7]
    detect_hw := command[8]
    match_mode := command[9]
    match_speed := command[10]

    current_match_mode := Format("{}", A_TitleMatchMode)
    current_match_speed := Format("{}", A_TitleMatchModeSpeed)
    if (match_mode != "") {
        SetTitleMatchMode, %match_mode%
    }
    if (match_speed != "") {
        SetTitleMatchMode, %match_speed%
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows, %detect_hw%
    }
    ControlSend, %ctrl%, %keys%, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
}



;
;BaseCheck(ByRef command) {
;    kommand := command[2]
;    title := command[3]
;    if %kommand%(title) {
;        return 1
;    }
;    else {
;        return 0
;    }
;}

FromMouse(ByRef command) {
    MouseGetPos,,, MouseWin
    return MouseWin
}

;WinGet(ByRef command) {
;    title := command[4]
;    text := command[5]
;    extitle := command[6]
;    extext := command[7]
;    WinGet, output,% command[3], %title%, %text%, %extitle%, %extext%
;    return output
;}

;WinSet(ByRef command) {
;    subcommand := command[2]
;    title := command[4]
;    value := command[3]
;
;    WinSet,%subcommand%,%value%,%title%
;}

;WinSetTitle(ByRef command) {
;    newtitle := command[4]
;    WinSetTitle,% command[2],, %newtitle%
;}

AHKWinIsAlwaysOnTop(ByRef command) {
    global BOOLEANRESPONSEMESSAGE
    title := command[2]
    WinGet, ExStyle, ExStyle, %title%
    if (ExStyle = "")
        return FormatNoValueResponse()

    if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    else
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
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
            s := Format("({}, {})", x, y)
        } else if (pos_info = "height") {
            s := Format("({})", height)
        } else if (pos_info = "width") {
            s := Format("({})", width)
        }
    } else {
        s := Format("({}, {}, {}, {})", x, y, width, height)
    }
    return s
}

CountNewlines(ByRef s) {
    newline := "`n"
    StringReplace, s, s, %newline%, %newline%, UseErrorLevel
    count := ErrorLevel
    return count
}

AHKEcho(ByRef command) {
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, command)
}


b64decode(ByRef pszString) {
    ; TODO load DLL globally for performance
    ; REF: https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptstringtobinaryw
    ;  [in]      LPCSTR pszString,  A pointer to a string that contains the formatted string to be converted.
    ;  [in]      DWORD  cchString,  The number of characters of the formatted string to be converted, not including the terminating NULL character. If this parameter is zero, pszString is considered to be a null-terminated string.
    ;  [in]      DWORD  dwFlags,    Indicates the format of the string to be converted. (see table in link above)
    ;  [in]      BYTE   *pbBinary,  A pointer to a buffer that receives the returned sequence of bytes. If this parameter is NULL, the function calculates the length of the buffer needed and returns the size, in bytes, of required memory in the DWORD pointed to by pcbBinary.
    ;  [in, out] DWORD  *pcbBinary, A pointer to a DWORD variable that, on entry, contains the size, in bytes, of the pbBinary buffer. After the function returns, this variable contains the number of bytes copied to the buffer. If this value is not large enough to contain all of the data, the function fails and GetLastError returns ERROR_MORE_DATA.
    ;  [out]     DWORD  *pdwSkip,   A pointer to a DWORD value that receives the number of characters skipped to reach the beginning of the -----BEGIN ...----- header. If no header is present, then the DWORD is set to zero. This parameter is optional and can be NULL if it is not needed.
    ;  [out]     DWORD  *pdwFlags   A pointer to a DWORD value that receives the flags actually used in the conversion. These are the same flags used for the dwFlags parameter. In many cases, these will be the same flags that were passed in the dwFlags parameter. If dwFlags contains one of the following flags, this value will receive a flag that indicates the actual format of the string. This parameter is optional and can be NULL if it is not needed.

    cchString := StrLen(pszString)
    dwFlags := 0x00000001  ; CRYPT_STRING_BASE64: Base64, without headers.
    getsize := 0 ; When this is NULL, the function returns the required size in bytes (for our first call, which is needed for our subsequent call)
    buff_size := 0 ; The function will write to this variable on our first call
    pdwSkip := 0 ; We don't use any headers or preamble, so this is zero
    pdwFlags := 0 ; We don't need this, so make it null


    ; The first call calculates the required size. The result is written to pbBinary
    success := DllCall("Crypt32.dll\CryptStringToBinary", "Ptr", &pszString, "UInt", cchString, "UInt", dwFlags, "UInt", getsize, "UIntP", buff_size, "Int", pdwSkip, "Int", pdwFlags )
    if (success = 0) {
        return ""
    }

    ; We're going to give a pointer to a variable to the next call, but first we want to make the buffer the correct size using VarSetCapacity using the previous return value
    VarSetCapacity(ret, buff_size, 0)

    ; Now that we know the buffer size we need and have the variable's capacity set to the proper size, we'll pass a pointer to the variable for the decoded value to be written to

    success := DllCall( "Crypt32.dll\CryptStringToBinary", "Ptr", &pszString, "UInt", cchString, "UInt", dwFlags, "Ptr", &ret, "UIntP", buff_size, "Int", pdwSkip, "Int", pdwFlags )
    if (success=0) {
        return ""
    }

    return StrGet(&ret, "UTF-8")
}

CommandArrayFromQuery(ByRef text) {
    decoded_commands := []
    encoded_array := StrSplit(text, "|")
    function_name := encoded_array[1]
    encoded_array.RemoveAt(1)
    decoded_commands.push(function_name)
    for index, encoded_value in encoded_array {
        decoded_value := b64decode(encoded_value)
        decoded_commands.push(decoded_value)
    }
    return decoded_commands
}

stdin  := FileOpen("*", "r `n", "UTF-8")  ; Requires [v1.1.17+]
response := ""

Loop {
    query := RTrim(stdin.ReadLine(), "`n")
    commandArray := CommandArrayFromQuery(query)
    try {
        func := commandArray[1]
        response := %func%(commandArray)
    } catch e {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, %e%)
    }

    if (response) {
        FileAppend, %response%, *, UTF-8
    } else {
        msg := FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("Unknown Error when calling {}", func))
        FileAppend, %msg%, *, UTF-8
    }
}
