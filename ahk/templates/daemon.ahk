{% block daemon_script %}
{% block directives %}
#NoEnv
#Persistent
#SingleInstance Off

; BEGIN user-defined directives
{% block user_directives %}
{% for directive in directives %}
{{ directive }}

{% endfor %}

; END user-defined directives
{% endblock user_directives %}
{% endblock directives %}

{% block message_types %}
{% for tom, name in message_types.items() %}
{{ name }} := "{{ tom }}"
{% endfor %}
{% endblock message_types %}


NOVALUE_SENTINEL := Chr(57344)

FormatResponse(ByRef MessageType, ByRef payload) {
    newline_count := CountNewlines(payload)
    response := Format("{}`n{}`n{}`n", MessageType, newline_count, payload)
    return response
}

FormatNoValueResponse() {
    global NOVALUE_SENTINEL
    global NOVALUERESPONSEMESSAGE
    return FormatResponse(NOVALUERESPONSEMESSAGE, NOVALUE_SENTINEL)
}

FormatBinaryResponse(ByRef bin) {
    global B64BINARYRESPONSEMESSAGE
    b64 := b64encode(bin)
    return FormatResponse(B64BINARYRESPONSEMESSAGE, b64)
}

AHKSetDetectHiddenWindows(ByRef command) {
    {% block AHKSetDetectHiddenWindows %}
    value := command[2]
    DetectHiddenWindows, %value%
    return FormatNoValueResponse()
    {% endblock AHKSetDetectHiddenWindows %}
}

AHKSetTitleMatchMode(ByRef command) {
    {% block AHKSetTitleMatchMode %}
    val1 := command[2]
    val2 := command[3]
    if (val1 != "") {
        SetTitleMatchMode, %val1%
    }
    if (val2 != "") {
        SetTitleMatchMode, %val2%
    }
    return FormatNoValueResponse()
    {% endblock AHKSetTitleMatchMode %}
}

AHKGetTitleMatchMode(ByRef command) {
    {% block AHKGetTitleMatchMode %}
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, A_TitleMatchMode)
    {% endblock AHKGetTitleMatchMode %}
}

AHKGetTitleMatchSpeed(ByRef command) {
    {% block AHKGetTitleMatchSpeed %}
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, A_TitleMatchModeSpeed)
    {% endblock AHKGetTitleMatchSpeed %}
}

AHKSetSendLevel(ByRef command) {
    {% block AHKSetSendLevel %}
    level := command[2]
    SendLevel, %level%
    return FormatNoValueResponse()
    {% endblock AHKSetSendLevel %}
}

AHKGetSendLevel(ByRef command) {
    {% block AHKGetSendLevel %}
    global INTEGERRESPONSEMESSAGE
    return FormatResponse(INTEGERRESPONSEMESSAGE, A_SendLevel)
    {% endblock AHKGetSendLevel %}
}

AHKWinExist(ByRef command) {
    {% block AHKWinExist %}
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

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinExist %}
}

AHKWinClose(ByRef command) {
    {% block AHKWinClose %}
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    secondstowait := command[9]

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

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    WinClose, %title%, %text%, %secondstowait%, %extitle%, %extext%

    return FormatNoValueResponse()
    {% endblock AHKWinClose %}
}

AHKWinKill(ByRef command) {
    {% block AHKWinKill %}
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    secondstowait := command[9]

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


    WinKill, %title%, %text%, %secondstowait%, %extitle%, %extext%

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinKill %}
}

AHKWinWait(ByRef command) {
    {% block AHKWinWait %}
    global WINDOWRESPONSEMESSAGE
    global TIMEOUTRESPONSEMESSAGE

    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    timeout := command[9]
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
    if (timeout != "") {
        WinWait, %title%, %text%, %timeout%, %extitle%, %extext%
    } else {
        WinWait, %title%, %text%,, %extitle%, %extext%
    }
    if (ErrorLevel = 1) {
        resp := FormatResponse(TIMEOUTRESPONSEMESSAGE, "WinWait timed out waiting for window")
    } else {
        WinGet, output, ID
        resp := FormatResponse(WINDOWRESPONSEMESSAGE, output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWait %}
}


AHKWinWaitActive(ByRef command) {
    {% block AHKWinWaitActive %}
    global WINDOWRESPONSEMESSAGE
    global TIMEOUTRESPONSEMESSAGE

    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    timeout := command[9]
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
    if (timeout != "") {
        WinWaitActive, %title%, %text%, %timeout%, %extitle%, %extext%
    } else {
        WinWaitActive, %title%, %text%,, %extitle%, %extext%
    }
    if (ErrorLevel = 1) {
        resp := FormatResponse(TIMEOUTRESPONSEMESSAGE, "WinWait timed out waiting for window")
    } else {
        WinGet, output, ID
        resp := FormatResponse(WINDOWRESPONSEMESSAGE, output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWaitActive %}
}


AHKWinWaitNotActive(ByRef command) {
    {% block AHKWinWaitNotActive %}
    global WINDOWRESPONSEMESSAGE
    global TIMEOUTRESPONSEMESSAGE

    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    timeout := command[9]
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
    if (timeout != "") {
        WinWaitNotActive, %title%, %text%, %timeout%, %extitle%, %extext%
    } else {
        WinWaitNotActive, %title%, %text%,, %extitle%, %extext%
    }
    if (ErrorLevel = 1) {
        resp := FormatResponse(TIMEOUTRESPONSEMESSAGE, "WinWait timed out waiting for window")
    } else {
        WinGet, output, ID
        resp := FormatResponse(WINDOWRESPONSEMESSAGE, output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWaitNotActive %}
}

AHKWinWaitClose(ByRef command) {
    {% block AHKWinWaitClose %}
    global TIMEOUTRESPONSEMESSAGE

    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    timeout := command[9]
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
    if (timeout != "") {
        WinWaitClose, %title%, %text%, %timeout%, %extitle%, %extext%
    } else {
        WinWaitClose, %title%, %text%,, %extitle%, %extext%
    }
    if (ErrorLevel = 1) {
        resp := FormatResponse(TIMEOUTRESPONSEMESSAGE, "WinWait timed out waiting for window")
    } else {
        resp := FormatNoValueResponse()
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWaitClose %}
}

AHKWinMinimize(ByRef command) {
    {% block AHKWinMinimize %}
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


    WinMinimize, %title%, %text%, %secondstowait%, %extitle%, %extext%

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinMinimize %}
}

AHKWinMaximize(ByRef command) {
    {% block AHKWinMaximize %}
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


    WinMaximize, %title%, %text%, %secondstowait%, %extitle%, %extext%

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinMaximize %}
}

AHKWinRestore(ByRef command) {
    {% block AHKWinRestore %}
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


    WinRestore, %title%, %text%, %secondstowait%, %extitle%, %extext%

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinRestore %}
}

AHKWinIsActive(ByRef command) {
    {% block AHKWinIsActive %}
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

    if WinActive(title, text, extitle, extext) {
        response := FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    } else {
        response := FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinIsActive %}
}

AHKWinGetID(ByRef command) {
    {% block AHKWinGetID %}
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
    {% endblock AHKWinGetID %}
}

AHKWinGetTitle(ByRef command) {
    {% block AHKWinGetTitle %}
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
    {% endblock AHKWinGetTitle %}
}

AHKWinGetIDLast(ByRef command) {
    {% block AHKWinGetIDLast %}
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
    {% endblock AHKWinGetIDLast %}
}


AHKWinGetPID(ByRef command) {
    {% block AHKWinGetPID %}
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
    {% endblock AHKWinGetPID %}
}


AHKWinGetProcessName(ByRef command) {
    {% block AHKWinGetProcessName %}
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
    {% endblock AHKWinGetProcessName %}
}

AHKWinGetProcessPath(ByRef command) {
    {% block AHKWinGetProcessPath %}
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
    {% endblock AHKWinGetProcessPath %}
}


AHKWinGetCount(ByRef command) {
    {% block AHKWinGetCount %}
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
    {% endblock AHKWinGetCount %}
}



AHKWinGetMinMax(ByRef command) {
    {% block AHKWinGetMinMax %}
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
    {% endblock AHKWinGetMinMax %}
}

AHKWinGetControlList(ByRef command) {
    {% block AHKWinGetControlList %}
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
    {% endblock AHKWinGetControlList %}
}

AHKWinGetTransparent(ByRef command) {
    {% block AHKWinGetTransparent %}
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
    {% endblock AHKWinGetTransparent %}
}
AHKWinGetTransColor(ByRef command) {
    {% block AHKWinGetTransColor %}
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
    {% endblock AHKWinGetTransColor %}
}
AHKWinGetStyle(ByRef command) {
    {% block AHKWinGetStyle %}
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
    {% endblock AHKWinGetStyle %}
}
AHKWinGetExStyle(ByRef command) {
    {% block AHKWinGetExStyle %}
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
    {% endblock AHKWinGetExStyle %}
}

AHKWinGetText(ByRef command) {
    {% block AHKWinGetText %}
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
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was an error getting window text")
    } else {
        response := FormatResponse(STRINGRESPONSEMESSAGE, output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetText %}
}



AHKWinSetTitle(ByRef command) {
    {% block AHKWinSetTitle %}
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
    {% endblock AHKWinSetTitle %}
}

AHKWinSetAlwaysOnTop(ByRef command) {
    {% block AHKWinSetAlwaysOnTop %}
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
    {% endblock AHKWinSetAlwaysOnTop %}
}

AHKWinSetBottom(ByRef command) {
    {% block AHKWinSetBottom %}
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
    {% endblock AHKWinSetBottom %}
}

AHKWinShow(ByRef command) {
    {% block AHKWinShow %}
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

    WinShow, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
    {% endblock AHKWinShow %}
}

AHKWinHide(ByRef command) {
    {% block AHKWinHide %}
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

    WinHide, %title%, %text%, %extitle%, %extext%
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return FormatNoValueResponse()
    {% endblock AHKWinHide %}
}


AHKWinSetTop(ByRef command) {
    {% block AHKWinSetTop %}
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
    {% endblock AHKWinSetTop %}
}

AHKWinSetEnable(ByRef command) {
    {% block AHKWinSetEnable %}
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
    {% endblock AHKWinSetEnable %}
}

AHKWinSetDisable(ByRef command) {
    {% block AHKWinSetDisable %}
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
    {% endblock AHKWinSetDisable %}
}

AHKWinSetRedraw(ByRef command) {
    {% block AHKWinSetRedraw %}
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
    {% endblock AHKWinSetRedraw %}
}

AHKWinSetStyle(ByRef command) {
    {% block AHKWinSetStyle %}
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
    if (ErrorLevel = 1) {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    } else {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWinSetStyle %}
}

AHKWinSetExStyle(ByRef command) {
    {% block AHKWinSetExStyle %}
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
    if (ErrorLevel = 1) {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    } else {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWinSetExStyle %}
}

AHKWinSetRegion(ByRef command) {
    {% block AHKWinSetRegion %}
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
    if (ErrorLevel = 1) {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    } else {
        resp := FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWinSetRegion %}
}

AHKWinSetTransparent(ByRef command) {
    {% block AHKWinSetTransparent %}
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
    {% endblock AHKWinSetTransparent %}
}

AHKWinSetTransColor(ByRef command) {
    {% block AHKWinSetTransColor %}
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
    {% endblock AHKWinSetTransColor %}
}

AHKImageSearch(ByRef command) {
    {% block AHKImageSearch %}
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
    {% endblock AHKImageSearch %}
}

AHKPixelGetColor(ByRef command) {
    {% block AHKPixelGetColor %}
    global STRINGRESPONSEMESSAGE
    x := command[2]
    y := command[3]
    coord_mode := command[4]
    options := command[5]

    current_mode := Format("{}", A_CoordModePixel)

    if (coord_mode != "") {
        CoordMode, Pixel, %coord_mode%
    }

    PixelGetColor, color, %x%, %y%, %options%
    ; TODO: check errorlevel

    if (coord_mode != "") {
        CoordMode, Pixel, %current_mode%
    }

    return FormatResponse(STRINGRESPONSEMESSAGE, color)
    {% endblock AHKPixelGetColor %}
}

AHKPixelSearch(ByRef command) {
    {% block AHKPixelSearch %}
    global COORDINATERESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    x1 := command[2]
    y1 := command[3]
    x2 := command[4]
    y2 := command[5]
    color := command[6]
    variation := command[7]
    options := command[8]
    coord_mode := command[9]

    current_mode := Format("{}", A_CoordModePixel)

    if (coord_mode != "") {
        CoordMode, Pixel, %coord_mode%
    }

    PixelSearch, resultx, resulty, %x1%, %y1%, %x2%, %y2%, %color%, %variation%, %options%

    if (coord_mode != "") {
        CoordMode, Pixel, %current_mode%
    }

    if (ErrorLevel = 1) {
        return FormatNoValueResponse()
    } else if (ErrorLevel = 0) {
        payload := Format("({}, {})", resultx, resulty)
        return FormatResponse(COORDINATERESPONSEMESSAGE, payload)
    } else if (ErrorLevel = 2) {
        return FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was a problem conducting the pixel search (ErrorLevel 2)")
    } else {
        return FormatResponse(EXCEPTIONRESPONSEMESSAGE, "Unexpected error. This is probably a bug. Please report this at https://github.com/spyoungtech/ahk/issues")
    }

    {% endblock AHKPixelSearch %}
}


AHKMouseGetPos(ByRef command) {
    {% block AHKMouseGetPos %}
    global COORDINATERESPONSEMESSAGE
    coord_mode := command[2]
    current_coord_mode := Format("{}", A_CoordModeMouse)
    if (coord_mode != "") {
        CoordMode, Mouse, %coord_mode%
    }
    MouseGetPos, xpos, ypos

    payload := Format("({}, {})", xpos, ypos)
    resp := FormatResponse(COORDINATERESPONSEMESSAGE, payload)

    if (coord_mode != "") {
        CoordMode, Mouse, %current_coord_mode%
    }

    return resp
    {% endblock AHKMouseGetPos %}
}

AHKKeyState(ByRef command) {
    {% block AHKKeyState %}
    global INTEGERRESPONSEMESSAGE
    global FLOATRESPONSEMESSAGE
    global STRINGRESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE

    keyname := command[2]
    mode := command[3]
    if (mode != "") {
        state := GetKeyState(keyname, mode)
    } else{
        state := GetKeyState(keyname)
    }

    if (state = "") {
        return FormatNoValueResponse()
    }

    if state is integer
        return FormatResponse(INTEGERRESPONSEMESSAGE, state)

    if state is float
        return FormatResponse(FLOATRESPONSEMESSAGE, state)

    if state is alnum
        return FormatResponse(STRINGRESPONSEMESSAGE, state)

    return FormatResponse(EXCEPTIONRESPONSEMESSAGE, state)
    {% endblock AHKKeyState %}
}

AHKMouseMove(ByRef command) {
    {% block AHKMouseMove %}
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
    {% endblock AHKMouseMove %}
}


AHKClick(ByRef command) {
    {% block AHKClick %}
    x := command[2]
    y := command[3]
    button := command[4]
    click_count := command[5]
    direction := command[6]
    r := command[7]
    relative_to := command[8]
    current_coord_rel := Format("{}", A_CoordModeMouse)

    if (relative_to != "") {
        CoordMode, Mouse, %relative_to%
    }

    Click, %x%, %y%, %button%, %direction%, %r%

    if (relative_to != "") {
        CoordMode, Mouse, %current_coord_rel%
    }

    return FormatNoValueResponse()

    {% endblock AHKClick %}
}

AHKGetCoordMode(ByRef command) {
    {% block AHKGetCoordMode %}
    global STRINGRESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    target := command[2]

    if (target = "ToolTip") {
        return FormatResponse(STRINGRESPONSEMESSAGE, A_CoordModeToolTip)
    }
    if (target = "Pixel") {
        return FormatResponse(STRINGRESPONSEMESSAGE, A_CoordModePixel)
    }
    if (target = "Mouse") {
        return FormatResponse(STRINGRESPONSEMESSAGE, A_CoordModeMouse)
    }
    if (target = "Caret") {
        return FormatResponse(STRINGRESPONSEMESSAGE, A_CoordModeCaret)
    }
    if (target = "Menu") {
        return FormatResponse(STRINGRESPONSEMESSAGE, A_CoordModeMenu)
    }
    return FormatResponse(EXCEPTIONRESPONSEMESSAGE, "Invalid coord mode")
    {% endblock AHKGetCoordMode %}
}

AHKSetCoordMode(ByRef command) {
    {% block AHKSetCoordMode %}
    target := command[2]
    relative_to := command[3]
    CoordMode, %target%, %relative_to%

    return FormatNoValueResponse()
    {% endblock AHKSetCoordMode %}
}

AHKMouseClickDrag(ByRef command) {
    {% block AHKMouseClickDrag %}
    button := command[2]
    x1 := command[3]
    y1 := command[4]
    x2 := command[5]
    y2 := command[6]
    speed := command[7]
    relative := command[8]
    relative_to := command[9]

    current_coord_rel := Format("{}", A_CoordModeMouse)

    if (relative_to != "") {
        CoordMode, Mouse, %relative_to%
    }

    MouseClickDrag, %button%, %x1%, %y1%, %x2%, %y2%, %speed%, %relative%

    if (relative_to != "") {
        CoordMode, Mouse, %current_coord_rel%
    }

    return FormatNoValueResponse()

    {% endblock AHKMouseClickDrag %}
}

AHKRegRead(ByRef command) {
    {% block RegRead %}
    global STRINGRESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    key_name := command[2]
    value_name := command[3]

    RegRead, output, %key_name%, %value_name%

    if (ErrorLevel = 1) {
        resp := FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("registry error: {}", A_LastError))
    }
    else {
        resp := FormatResponse(STRINGRESPONSEMESSAGE, Format("{}", output))
    }
    return resp
    {% endblock RegRead %}
}



AHKRegWrite(ByRef command) {
    {% block RegWrite %}
    global EXCEPTIONRESPONSEMESSAGE
    value_type := command[2]
    key_name := command[3]
    value_name := command[4]
    value := command[5]
    RegWrite, %value_type%, %key_name%, %value_name%, %value%
    if (ErrorLevel = 1) {
        return FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("registry error: {}", A_LastError))
    }

    return FormatNoValueResponse()
    {% endblock RegWrite %}
}

AHKRegDelete(ByRef command) {
    {% block RegDelete %}
    global EXCEPTIONRESPONSEMESSAGE
    key_name := command[2]
    value_name := command[3]
    RegDelete, %key_name%, %value_name%
    if (ErrorLevel = 1) {
        return FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("registry error: {}", A_LastError))
    }
    return FormatNoValueResponse()

    {% endblock RegDelete %}
}

AHKKeyWait(ByRef command) {
    {% block AHKKeyWait %}
    global INTEGERRESPONSEMESSAGE
    keyname := command[2]
    if (command.Length() = 2) {
        KeyWait,% keyname
    } else {
        options := command[3]
        KeyWait,% keyname,% options
    }
    return FormatResponse(INTEGERRESPONSEMESSAGE, ErrorLevel)
    {% endblock AHKKeyWait %}
}

SetKeyDelay(ByRef command) {
    {% block SetKeyDelay %}
    SetKeyDelay, command[2], command[3]
    {% endblock SetKeyDelay %}
}



AHKSend(ByRef command) {
    {% block AHKSend %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%
    }

    Send,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }
    return FormatNoValueResponse()
    {% endblock AHKSend %}
}

AHKSendRaw(ByRef command) {
    {% block AHKSendRaw %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%
    }

    SendRaw,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }
    return FormatNoValueResponse()
    {% endblock AHKSendRaw %}
}

AHKSendInput(ByRef command) {
    {% block AHKSendInput %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%
    }

    SendInput,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }
    return FormatNoValueResponse()
    {% endblock AHKSendInput %}
}


AHKSendEvent(ByRef command) {
    {% block AHKSendEvent %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%
    }

    SendEvent,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }
    return FormatNoValueResponse()
    {% endblock AHKSendEvent %}
}

AHKSendPlay(ByRef command) {
    {% block AHKSendPlay %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelayPlay)
    current_key_duration := Format("{}", A_KeyDurationPlay)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%, Play
    }

    SendPlay,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }
    return FormatNoValueResponse()
    {% endblock AHKSendPlay %}
}

AHKSetCapsLockState(ByRef command) {
    {% block AHKSetCapsLockState %}
    state := command[2]
    if (state = "") {
        SetCapsLockState % !GetKeyState("CapsLock", "T")
    } else {
        SetCapsLockState, %state%
    }
    return FormatNoValueResponse()
    {% endblock AHKSetCapsLockState %}
}

HideTrayTip(ByRef command) {
    {% block HideTrayTip %}
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        Menu Tray, NoIcon
        Sleep 200 ; It may be necessary to adjust this sleep.
        Menu Tray, Icon
    }
    {% endblock HideTrayTip %}
}




AHKWinGetClass(ByRef command) {
    {% block AHKWinGetClass %}
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

    WinGetClass, output,%title%,%text%,%extitle%,%extext%

    if (ErrorLevel = 1) {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was an error getting window class")
    } else {
        response := FormatResponse(STRINGRESPONSEMESSAGE, output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetClass %}
}

AHKWinActivate(ByRef command) {
    {% block AHKWinActivate %}
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

    WinActivate, %title%, %text%, %extitle%, %extext%

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinActivate %}
}




AHKWindowList(ByRef command) {
    {% block AHKWindowList %}
    global WINDOWLISTRESPONSEMESSAGE

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

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
    if (detect_hw) {
        DetectHiddenWindows, %detect_hw%
    }

    WinGet windows, List, %title%, %text%, %extitle%, %extext%
    r := ""
    Loop %windows%
    {
        id := windows%A_Index%
        r .= id . "`,"
    }
    resp := FormatResponse(WINDOWLISTRESPONSEMESSAGE, r)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWindowList %}
}



AHKControlClick(ByRef command) {
    {% block AHKControlClick %}
    global EXCEPTIONRESPONSEMESSAGE
    ctrl := command[2]
    title := command[3]
    text := command[4]
    button := command[5]
    click_count := command[6]
    options := command[7]
    exclude_title := command[8]
    exclude_text := command[9]
    detect_hw := command[10]
    match_mode := command[11]
    match_speed := command[12]

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

    ControlClick, %ctrl%, %title%, %text%, %button%, %click_count%, %options%, %exclude_title%, %exclude_text%

    if (ErrorLevel != 0) {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "Failed to click control")
    } else {
        response := FormatNoValueResponse()
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response
    {% endblock AHKControlClick %}
}

AHKControlGetText(ByRef command) {
    {% block AHKControlGetText %}
    global STRINGRESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    ctrl := command[2]
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

    ControlGetText, result, %ctrl%, %title%, %text%, %extitle%, %extext%

    if (ErrorLevel = 1) {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was a problem getting the text")
    } else {
        response := FormatResponse(STRINGRESPONSEMESSAGE, result)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response
    {% endblock AHKControlGetText %}
}


AHKControlGetPos(ByRef command) {
    {% block AHKControlGetPos %}
    global POSITIONRESPONSEMESSAGE
    global EXCEPTIONRESPONSEMESSAGE
    ctrl := command[2]
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

    ControlGetPos, x, y, w, h, %ctrl%, %title%, %text%, %extitle%, %extext%
    if (ErrorLevel = 1) {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was a problem getting the text")
    } else {
        result := Format("({1:i}, {2:i}, {3:i}, {4:i})", x, y, w, h)
        response := FormatResponse(PositionResponseMessage, result)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response


    {% endblock AHKControlGetPos %}
}

AHKControlSend(ByRef command) {
    {% block AHKControlSend %}
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
    {% endblock AHKControlSend %}
}




AHKWinFromMouse(ByRef command) {
    {% block AHKWinFromMouse %}
    global WINDOWRESPONSEMESSAGE
    MouseGetPos,,, MouseWin

    if (MouseWin = "") {
        return FormatNoValueResponse()
    }

    return FormatResponse(WINDOWRESPONSEMESSAGE, MouseWin)
    {% endblock AHKWinFromMouse %}
}


AHKWinIsAlwaysOnTop(ByRef command) {
    {% block AHKWinIsAlwaysOnTop %}
    global BOOLEANRESPONSEMESSAGE
    title := command[2]
    WinGet, ExStyle, ExStyle, %title%
    if (ExStyle = "")
        return FormatNoValueResponse()

    if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 1)
    else
        return FormatResponse(BOOLEANRESPONSEMESSAGE, 0)
    {% endblock AHKWinIsAlwaysOnTop %}
}


AHKWinMove(ByRef command) {
    {% block AHKWinMove %}
    title := command[2]
    text := command[3]
    extitle := command[4]
    extext := command[5]
    detect_hw := command[6]
    match_mode := command[7]
    match_speed := command[8]
    x := command[9]
    y := command[10]
    width := command[11]
    height := command[12]

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

    WinMove, %title%, %text%, %x%, %y%, %width%, %height%, %extitle%, %extext%

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()

    {% endblock AHKWinMove %}
}

AHKWinGetPos(ByRef command) {
    {% block AHKWinGetPos %}
    global POSITIONRESPONSEMESSAGE
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

    WinGetPos, x, y, w, h, %title%, %text%, %extitle%, %extext%

    if (ErrorLevel = 1) {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, "There was a problem getting the position")
    } else {
        result := Format("({1:i}, {2:i}, {3:i}, {4:i})", x, y, w, h)
        response := FormatResponse(PositionResponseMessage, result)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response
    {% endblock AHKWinGetPos %}
}


AHKGetVolume(ByRef command) {
    {% block AHKGetVolume %}
    global EXCEPTIONRESPONSEMESSAGE
    global FLOATRESPONSEMESSAGE
    device_number := command[2]

    try {
    SoundGetWaveVolume, retval, %device_number%
    } catch e {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("There was a problem getting the volume with device of index {} ({})", device_number, e.message))
        return response
    }
    if (ErrorLevel = 1) {
        response := FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("There was a problem getting the volume with device of index {}", device_number))
    } else {
        response := FormatResponse(FLOATRESPONSEMESSAGE, Format("{}", retval))
    }
    return response
    {% endblock AHKGetVolume %}
}

AHKSoundBeep(ByRef command) {
    {% block AHKSoundBeep %}
    freq := command[2]
    duration := command[3]
    SoundBeep , %freq%, %duration%
    return FormatNoValueResponse()
    {% endblock AHKSoundBeep %}
}

AHKSoundGet(ByRef command) {
    {% block AHKSoundGet %}
    global STRINGRESPONSEMESSAGE
    device_number := command[2]
    component_type := command[3]
    control_type := command[4]

    SoundGet, retval, %component_type%, %control_type%, %device_number%
    ; TODO interpret return type
    return FormatResponse(STRINGRESPONSEMESSAGE, Format("{}", retval))
    {% endblock AHKSoundGet %}
}

AHKSoundSet(ByRef command) {
    {% block AHKSoundSet %}
    device_number := command[2]
    component_type := command[3]
    control_type := command[4]
    value := command[5]
    SoundSet, %value%, %component_type%, %control_type%, %device_number%
    return FormatNoValueResponse()
    {% endblock AHKSoundSet %}
}

AHKSoundPlay(ByRef command) {
    {% block AHKSoundPlay %}
    filename := command[2]
    SoundPlay, %filename%
    return FormatNoValueResponse()
    {% endblock AHKSoundPlay %}
}

AHKSetVolume(ByRef command) {
    {% block AHKSetVolume %}
    device_number := command[2]
    value := command[3]
    SoundSetWaveVolume, %value%, %device_number%
    return FormatNoValueResponse()
    {% endblock AHKSetVolume %}
}

CountNewlines(ByRef s) {
    newline := "`n"
    StringReplace, s, s, %newline%, %newline%, UseErrorLevel
    count := ErrorLevel
    return count
}

AHKEcho(ByRef command) {
    {% block AHKEcho %}
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, command)
    {% endblock AHKEcho %}
}

AHKTraytip(ByRef command) {
    {% block AHKTraytip %}
    title := command[2]
    text := command[3]
    second := command[4]
    option := command[5]

    TrayTip, %title%, %text%, %second%, %option%
    return FormatNoValueResponse()
    {% endblock AHKTraytip %}
}

AHKShowToolTip(ByRef command) {
    {% block AHKShowToolTip %}
    text := command[2]
    x := command[3]
    y := command[4]
    which := command[5]
    ToolTip, %text%, %x%, %y%, %which%
    return FormatNoValueResponse()
    {% endblock AHKShowToolTip %}
}

AHKGetClipboard(ByRef command) {
    {% block AHKGetClipboard %}
    global STRINGRESPONSEMESSAGE
    return FormatResponse(STRINGRESPONSEMESSAGE, Clipboard)
    {% endblock AHKGetClipboard %}
}

AHKGetClipboardAll(ByRef command) {
    {% block AHKGetClipboardAll %}
    data := ClipboardAll
    return FormatBinaryResponse(data)
    {% endblock AHKGetClipboardAll %}
}

AHKSetClipboard(ByRef command) {
    {% block AHKSetClipboard %}
    text := command[2]
    Clipboard := text
    return FormatNoValueResponse()
    {% endblock AHKSetClipboard %}
}

AHKSetClipboardAll(ByRef command) {
    {% block AHKSetClipboardAll %}
    ; TODO there should be a way for us to accept a base64 string instead
    filename := command[2]
    FileRead, Clipboard, %filename%
    return FormatNoValueResponse()
    {% endblock AHKSetClipboardAll %}
}

AHKClipWait(ByRef command) {
    global TIMEOUTRESPONSEMESSAGE
    timeout := command[2]
    wait_for_any_data := command[3]


    ClipWait, %timeout%, %wait_for_any_data%

    if (ErrorLevel = 1) {
        return FormatResponse(TIMEOUTRESPONSEMESSAGE, "timed out waiting for clipboard data")
    }
    return FormatNoValueResponse()
}

AHKBlockInput(ByRef command) {
    value := command[2]
    BlockInput, %value%
    return FormatNoValueResponse()
}

AHKMenuTrayTip(ByRef command) {
    value := command[2]
    Menu, Tray, Tip, %value%
    return FormatNoValueResponse()
}

AHKMenuTrayShow(ByRef command) {
    Menu, Tray, Icon
    return FormatNoValueResponse()
}

AHKMenuTrayIcon(ByRef command) {
    filename := command[2]
    icon_number := command[3]
    freeze := command[4]
    Menu, Tray, Icon, %filename%, %icon_number%,%freeze%
    return FormatNoValueResponse()
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

    if (pszString = "") {
        return ""
    }

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

b64encode(ByRef data) {
    ; REF: https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptbinarytostringa
    ;  [in]            const BYTE *pbBinary: A pointer to the array of bytes to be converted into a string.
    ;  [in]            DWORD      cbBinary: The number of elements in the pbBinary array.
    ;  [in]            DWORD      dwFlags: Specifies the format of the resulting formatted string (see table in REF)
    ;  [out, optional] LPSTR      pszString: A pointer to the string, or null (0) to calculate size
    ;  [in, out]       DWORD      *pcchString: A pointer to a DWORD variable that contains the size, in TCHARs, of the pszString buffer


    cbBinary := StrLen(data) * (A_IsUnicode ? 2 : 1)
    if (cbBinary = 0) {
        return ""
    }
    dwFlags := 0x00000001 | 0x40000000  ; CRYPT_STRING_BASE64 + CRYPT_STRING_NOCRLF

    ; First step is to get the size so we can set the capacity of our return buffer correctly
    success := DllCall("Crypt32.dll\CryptBinaryToString", "Ptr", &data, "UInt", cbBinary, "UInt", dwFlags, "Ptr", 0, "UIntP", buff_size)
    if (success = 0) {
        msg := Format("Problem converting data to base64 when calling CryptBinaryToString ({})", A_LastError)
        throw Exception(msg, -1)
    }


    VarSetCapacity(ret, buff_size * (A_IsUnicode ? 2 : 1))

    ; Now we do the conversion to base64 and rteturn the string

    success := DllCall("Crypt32.dll\CryptBinaryToString", "Ptr", &data, "UInt", cbBinary, "UInt", dwFlags, "Str", ret, "UIntP", buff_size)
    if (success = 0) {
        msg := Format("Problem converting data to base64 when calling CryptBinaryToString ({})", A_LastError)
        throw Exception(msg, -1)
    }
    return ret
}


; End of included content

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


{% block before_autoexecute %}
{% endblock before_autoexecute %}

{% block autoexecute %}
stdin  := FileOpen("*", "r `n", "UTF-8")  ; Requires [v1.1.17+]
pyresp := ""

Loop {
    query := RTrim(stdin.ReadLine(), "`n")
    commandArray := CommandArrayFromQuery(query)
    try {
        func := commandArray[1]
        {% block before_function %}
        {% endblock before_function %}
        pyresp := %func%(commandArray)
        {% block after_function %}
        {% endblock after_function %}
    } catch e {
        {% block function_error_handle %}
        message := Format("Error occurred in {}. The error message was: {}", e.What, e.message)
        pyresp := FormatResponse(EXCEPTIONRESPONSEMESSAGE, message)
        {% endblock function_error_handle %}
    }
    {% block send_response %}
    if (pyresp) {
        FileAppend, %pyresp%, *, UTF-8
    } else {
        msg := FormatResponse(EXCEPTIONRESPONSEMESSAGE, Format("Unknown Error when calling {}", func))
        FileAppend, %msg%, *, UTF-8
    }
    {% endblock send_response %}
}
{% endblock autoexecute %}
{% endblock daemon_script %}
