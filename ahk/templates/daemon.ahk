{% block daemon_script %}
{% block directives %}
#Requires AutoHotkey v1.1.17+
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

Critical, 100

{% block message_types %}
MESSAGE_TYPES := Object({% for tom, msg_class in message_registry.items() %}"{{ msg_class.fqn() }}", "{{ tom.decode('utf-8') }}"{% if not loop.last %}, {% endif %}{% endfor %})
{% endblock message_types %}

NOVALUE_SENTINEL := Chr(57344)

FormatResponse(ByRef MessageType, ByRef payload) {
    global MESSAGE_TYPES
    newline_count := CountNewlines(payload)
    response := Format("{}`n{}`n{}`n", MESSAGE_TYPES[MessageType], newline_count, payload)
    return response
}

FormatNoValueResponse() {
    global NOVALUE_SENTINEL
    return FormatResponse("ahk.message.NoValueResponseMessage", NOVALUE_SENTINEL)
}

FormatBinaryResponse(ByRef bin) {
    b64 := b64encode(bin)
    return FormatResponse("ahk.message.B64BinaryResponseMessage", b64)
}

AHKSetDetectHiddenWindows(args*) {
    {% block AHKSetDetectHiddenWindows %}
    value := args[1]
    DetectHiddenWindows, %value%
    return FormatNoValueResponse()
    {% endblock AHKSetDetectHiddenWindows %}
}

AHKSetTitleMatchMode(args*) {
    {% block AHKSetTitleMatchMode %}
    val1 := args[1]
    val2 := args[2]
    if (val1 != "") {
        SetTitleMatchMode, %val1%
    }
    if (val2 != "") {
        SetTitleMatchMode, %val2%
    }
    return FormatNoValueResponse()
    {% endblock AHKSetTitleMatchMode %}
}

AHKGetTitleMatchMode(args*) {
    {% block AHKGetTitleMatchMode %}

    return FormatResponse("ahk.message.StringResponseMessage", A_TitleMatchMode)
    {% endblock AHKGetTitleMatchMode %}
}

AHKGetTitleMatchSpeed(args*) {
    {% block AHKGetTitleMatchSpeed %}

    return FormatResponse("ahk.message.StringResponseMessage", A_TitleMatchModeSpeed)
    {% endblock AHKGetTitleMatchSpeed %}
}

AHKSetSendLevel(args*) {
    {% block AHKSetSendLevel %}
    level := args[1]
    SendLevel, %level%
    return FormatNoValueResponse()
    {% endblock AHKSetSendLevel %}
}

AHKGetSendLevel(args*) {
    {% block AHKGetSendLevel %}

    return FormatResponse("ahk.message.IntegerResponseMessage", A_SendLevel)
    {% endblock AHKGetSendLevel %}
}

AHKWinExist(args*) {
    {% block AHKWinExist %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 1)
    } else {
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 0)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinExist %}
}

AHKWinClose(args*) {
    {% block AHKWinClose %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    secondstowait := args[8]

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

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinClose %}
}

AHKWinKill(args*) {
    {% block AHKWinKill %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    secondstowait := args[8]

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

AHKWinWait(args*) {
    {% block AHKWinWait %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    timeout := args[8]
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
        resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
    } else {
        WinGet, output, ID
        resp := FormatResponse("ahk.message.WindowResponseMessage", output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWait %}
}

AHKWinWaitActive(args*) {
    {% block AHKWinWaitActive %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    timeout := args[8]
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
        resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
    } else {
        WinGet, output, ID
        resp := FormatResponse("ahk.message.WindowResponseMessage", output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWaitActive %}
}

AHKWinWaitNotActive(args*) {
    {% block AHKWinWaitNotActive %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    timeout := args[8]
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
        resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
    } else {
        WinGet, output, ID
        resp := FormatResponse("ahk.message.WindowResponseMessage", output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWaitNotActive %}
}

AHKWinWaitClose(args*) {
    {% block AHKWinWaitClose %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    timeout := args[8]
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
        resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
    } else {
        resp := FormatNoValueResponse()
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return resp
    {% endblock AHKWinWaitClose %}
}

AHKWinMinimize(args*) {
    {% block AHKWinMinimize %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinMaximize(args*) {
    {% block AHKWinMaximize %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinRestore(args*) {
    {% block AHKWinRestore %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinIsActive(args*) {
    {% block AHKWinIsActive %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
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
        response := FormatResponse("ahk.message.BooleanResponseMessage", 1)
    } else {
        response := FormatResponse("ahk.message.BooleanResponseMessage", 0)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinIsActive %}
}

AHKWinGetID(args*) {
    {% block AHKWinGetID %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.WindowResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetID %}
}

AHKWinGetTitle(args*) {
    {% block AHKWinGetTitle %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

    return FormatResponse("ahk.message.StringResponseMessage", text)
    {% endblock AHKWinGetTitle %}
}

AHKWinGetIDLast(args*) {
    {% block AHKWinGetIDLast %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.WindowResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetIDLast %}
}

AHKWinGetPID(args*) {
    {% block AHKWinGetPID %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.IntegerResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetPID %}
}

AHKWinGetProcessName(args*) {
    {% block AHKWinGetProcessName %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetProcessName %}
}

AHKWinGetProcessPath(args*) {
    {% block AHKWinGetProcessPath %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetProcessPath %}
}

AHKWinGetCount(args*) {
    {% block AHKWinGetCount %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.IntegerResponseMessage", output)
    } else {
        response := FormatResponse("ahk.message.IntegerResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetCount %}
}

AHKWinGetMinMax(args*) {
    {% block AHKWinGetMinMax %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.IntegerResponseMessage", output)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetMinMax %}
}

AHKWinGetControlList(args*) {
    {% block AHKWinGetControlList %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        return FormatResponse("ahk.message.WindowControlListResponseMessage", Format("('{}', [])", ahkid))
    }

    ctrListArr := StrSplit(ctrList, "`n")
    ctrListIDArr := StrSplit(ctrListID, "`n")
    if (ctrListArr.Length() != ctrListIDArr.Length()) {
        DetectHiddenWindows, %current_detect_hw%
        SetTitleMatchMode, %current_match_mode%
        SetTitleMatchMode, %current_match_speed%
        return FormatResponse("ahk.message.ExceptionResponseMessage", "Control hwnd/class lists have unexpected lengths")
    }

    output := Format("('{}', [", ahkid)

    for index, hwnd in ctrListIDArr {
        classname := ctrListArr[index]
        output .= Format("('{}', '{}'), ", hwnd, classname)

    }
    output .= "])"
    response := FormatResponse("ahk.message.WindowControlListResponseMessage", output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetControlList %}
}

AHKWinGetTransparent(args*) {
    {% block AHKWinGetTransparent %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
    response := FormatResponse("ahk.message.IntegerResponseMessage", output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetTransparent %}
}
AHKWinGetTransColor(args*) {
    {% block AHKWinGetTransColor %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
    response := FormatResponse("ahk.message.NoValueResponseMessage", output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetTransColor %}
}
AHKWinGetStyle(args*) {
    {% block AHKWinGetStyle %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
    response := FormatResponse("ahk.message.NoValueResponseMessage", output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetStyle %}
}
AHKWinGetExStyle(args*) {
    {% block AHKWinGetExStyle %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
    response := FormatResponse("ahk.message.NoValueResponseMessage", output)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetExStyle %}
}

AHKWinGetText(args*) {
    {% block AHKWinGetText %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.ExceptionResponseMessage", "There was an error getting window text")
    } else {
        response := FormatResponse("ahk.message.StringResponseMessage", output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetText %}
}

AHKWinSetTitle(args*) {
    {% block AHKWinSetTitle %}
    new_title := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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

AHKWinSetAlwaysOnTop(args*) {
    {% block AHKWinSetAlwaysOnTop %}
    toggle := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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

AHKWinSetBottom(args*) {
    {% block AHKWinSetBottom %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinShow(args*) {
    {% block AHKWinShow %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinHide(args*) {
    {% block AHKWinHide %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinSetTop(args*) {
    {% block AHKWinSetTop %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinSetEnable(args*) {
    {% block AHKWinSetEnable %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinSetDisable(args*) {
    {% block AHKWinSetDisable %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinSetRedraw(args*) {
    {% block AHKWinSetRedraw %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWinSetStyle(args*) {
    {% block AHKWinSetStyle %}

    style := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 0)
    } else {
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 1)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWinSetStyle %}
}

AHKWinSetExStyle(args*) {
    {% block AHKWinSetExStyle %}

    style := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 0)
    } else {
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 1)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWinSetExStyle %}
}

AHKWinSetRegion(args*) {
    {% block AHKWinSetRegion %}

    options := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 0)
    } else {
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 1)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWinSetRegion %}
}

AHKWinSetTransparent(args*) {
    {% block AHKWinSetTransparent %}

    transparency := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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

AHKWinSetTransColor(args*) {
    {% block AHKWinSetTransColor %}

    color := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return FormatNoValueResponse()
    {% endblock AHKWinSetTransColor %}
}

AHKImageSearch(args*) {
    {% block AHKImageSearch %}

    imagepath := args[5]
    x1 := args[1]
    y1 := args[2]
    x2 := args[3]
    y2 := args[4]
    coord_mode := args[6]

    current_mode := Format("{}", A_CoordModePixel)

    if (coord_mode != "") {
        CoordMode, Pixel, %coord_mode%
    }

    if (x2 = "A_ScreenWidth") {
        x2 := A_ScreenWidth
    }
    if (y2 = "A_ScreenHeight") {
        y2 := A_ScreenHeight
    }

    ImageSearch, xpos, ypos,% x1,% y1,% x2,% y2, %imagepath%

    if (coord_mode != "") {
        CoordMode, Pixel, %current_mode%
    }

    if (ErrorLevel = 2) {
        s := FormatResponse("ahk.message.ExceptionResponseMessage", "there was a problem that prevented the args from conducting the search (such as failure to open the image file or a badly formatted option)")
    } else if (ErrorLevel = 1) {
        s := FormatNoValueResponse()
    } else {
        s := FormatResponse("ahk.message.CoordinateResponseMessage", Format("({}, {})", xpos, ypos))
    }

    return s
    {% endblock AHKImageSearch %}
}

AHKPixelGetColor(args*) {
    {% block AHKPixelGetColor %}

    x := args[1]
    y := args[2]
    coord_mode := args[3]
    options := args[4]

    current_mode := Format("{}", A_CoordModePixel)

    if (coord_mode != "") {
        CoordMode, Pixel, %coord_mode%
    }

    PixelGetColor, color, %x%, %y%, %options%
    ; TODO: check errorlevel

    if (coord_mode != "") {
        CoordMode, Pixel, %current_mode%
    }

    return FormatResponse("ahk.message.StringResponseMessage", color)
    {% endblock AHKPixelGetColor %}
}

AHKPixelSearch(args*) {
    {% block AHKPixelSearch %}

    x1 := args[1]
    y1 := args[2]
    x2 := args[3]
    y2 := args[4]
    color := args[5]
    variation := args[6]
    options := args[7]
    coord_mode := args[8]

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
        return FormatResponse("ahk.message.CoordinateResponseMessage", payload)
    } else if (ErrorLevel = 2) {
        return FormatResponse("ahk.message.ExceptionResponseMessage", "There was a problem conducting the pixel search (ErrorLevel 2)")
    } else {
        return FormatResponse("ahk.message.ExceptionResponseMessage", "Unexpected error. This is probably a bug. Please report this at https://github.com/spyoungtech/ahk/issues")
    }

    {% endblock AHKPixelSearch %}
}

AHKMouseGetPos(args*) {
    {% block AHKMouseGetPos %}

    coord_mode := args[1]
    current_coord_mode := Format("{}", A_CoordModeMouse)
    if (coord_mode != "") {
        CoordMode, Mouse, %coord_mode%
    }
    MouseGetPos, xpos, ypos

    payload := Format("({}, {})", xpos, ypos)
    resp := FormatResponse("ahk.message.CoordinateResponseMessage", payload)

    if (coord_mode != "") {
        CoordMode, Mouse, %current_coord_mode%
    }

    return resp
    {% endblock AHKMouseGetPos %}
}

AHKKeyState(args*) {
    {% block AHKKeyState %}

    keyname := args[1]
    mode := args[2]
    if (mode != "") {
        state := GetKeyState(keyname, mode)
    } else{
        state := GetKeyState(keyname)
    }

    if (state = "") {
        return FormatNoValueResponse()
    }

    if state is integer
        return FormatResponse("ahk.message.IntegerResponseMessage", state)

    if state is float
        return FormatResponse("ahk.message.FloatResponseMessage", state)

    return FormatResponse("ahk.message.StringResponseMessage", state)

    {% endblock AHKKeyState %}
}

AHKMouseMove(args*) {
    {% block AHKMouseMove %}
    x := args[1]
    y := args[2]
    speed := args[3]
    relative := args[4]
    send_mode := args[5]
    coord_mode := args[6]

    current_send_mode := Format("{}", A_SendMode)
    current_coord_mode := Format("{}", A_CoordModeMouse)

    if (send_mode != "") {
        SendMode, %send_mode%
    }

    if (coord_mode != "") {
        CoordMode, Mouse, %coord_mode%
    }

    if (relative != "") {
    MouseMove, %x%, %y%, %speed%, R
    } else {
    MouseMove, %x%, %y%, %speed%
    }

    if (send_mode != "") {
        SendMode, %current_send_mode%
    }

    if (coord_mode != "") {
        CoordMode, Mouse, %current_coord_mode%
    }

    resp := FormatNoValueResponse()
    return resp
    {% endblock AHKMouseMove %}
}

AHKClick(args*) {
    {% block AHKClick %}
    x := args[1]
    y := args[2]
    button := args[3]
    click_count := args[4]
    direction := args[5]
    r := args[6]
    relative_to := args[7]
    send_mode := args[8]
    current_coord_rel := Format("{}", A_CoordModeMouse)
    current_send_mode := Format("{}", A_SendMode)

    if (send_mode != "") {
        SendMode, %send_mode%
    }

    if (relative_to != "") {
        CoordMode, Mouse, %relative_to%
    }


    Click, %x%, %y%, %button%, %direction%, %r%

   if (send_mode != "") {
        SendMode, %current_send_mode%
    }

    if (relative_to != "") {
        CoordMode, Mouse, %current_coord_rel%
    }

    return FormatNoValueResponse()

    {% endblock AHKClick %}
}

AHKGetCoordMode(args*) {
    {% block AHKGetCoordMode %}

    target := args[1]

    if (target = "ToolTip") {
        return FormatResponse("ahk.message.StringResponseMessage", A_CoordModeToolTip)
    }
    if (target = "Pixel") {
        return FormatResponse("ahk.message.StringResponseMessage", A_CoordModePixel)
    }
    if (target = "Mouse") {
        return FormatResponse("ahk.message.StringResponseMessage", A_CoordModeMouse)
    }
    if (target = "Caret") {
        return FormatResponse("ahk.message.StringResponseMessage", A_CoordModeCaret)
    }
    if (target = "Menu") {
        return FormatResponse("ahk.message.StringResponseMessage", A_CoordModeMenu)
    }
    return FormatResponse("ahk.message.ExceptionResponseMessage", "Invalid coord mode")
    {% endblock AHKGetCoordMode %}
}

AHKSetCoordMode(args*) {
    {% block AHKSetCoordMode %}
    target := args[1]
    relative_to := args[2]
    CoordMode, %target%, %relative_to%

    return FormatNoValueResponse()
    {% endblock AHKSetCoordMode %}
}

AHKGetSendMode(args*) {
    return FormatResponse("ahk.message.StringResponseMessage", A_SendMode)
}


AHKSetSendMode(args*) {
    mode := args[1]
    SendMode, %mode%
    return FormatNoValueResponse()
}


AHKMouseClickDrag(args*) {
    {% block AHKMouseClickDrag %}
    button := args[1]
    x1 := args[2]
    y1 := args[3]
    x2 := args[4]
    y2 := args[5]
    speed := args[6]
    relative := args[7]
    relative_to := args[8]
    send_mode := args[8]
    current_send_mode := Format("{}", A_SendMode)
   if (send_mode != "") {
        SendMode, %send_mode%
    }

    current_coord_rel := Format("{}", A_CoordModeMouse)

    if (relative_to != "") {
        CoordMode, Mouse, %relative_to%
    }

    MouseClickDrag, %button%, %x1%, %y1%, %x2%, %y2%, %speed%, %relative%

    if (relative_to != "") {
        CoordMode, Mouse, %current_coord_rel%
    }

   if (send_mode != "") {
        SendMode, %current_send_mode%
    }

    return FormatNoValueResponse()

    {% endblock AHKMouseClickDrag %}
}

AHKRegRead(args*) {
    {% block RegRead %}

    key_name := args[1]
    value_name := args[2]

    RegRead, output, %key_name%, %value_name%

    if (ErrorLevel = 1) {
        resp := FormatResponse("ahk.message.ExceptionResponseMessage", Format("registry error: {}", A_LastError))
    }
    else {
        resp := FormatResponse("ahk.message.StringResponseMessage", Format("{}", output))
    }
    return resp
    {% endblock RegRead %}
}

AHKRegWrite(args*) {
    {% block RegWrite %}

    value_type := args[1]
    key_name := args[2]
    value_name := args[3]
    value := args[4]
    RegWrite, %value_type%, %key_name%, %value_name%, %value%
    if (ErrorLevel = 1) {
        return FormatResponse("ahk.message.ExceptionResponseMessage", Format("registry error: {}", A_LastError))
    }

    return FormatNoValueResponse()
    {% endblock RegWrite %}
}

AHKRegDelete(args*) {
    {% block RegDelete %}

    key_name := args[1]
    value_name := args[2]
    RegDelete, %key_name%, %value_name%
    if (ErrorLevel = 1) {
        return FormatResponse("ahk.message.ExceptionResponseMessage", Format("registry error: {}", A_LastError))
    }
    return FormatNoValueResponse()

    {% endblock RegDelete %}
}

AHKKeyWait(args*) {
    {% block AHKKeyWait %}

    keyname := args[1]
    options := args[2]

    if (options = "") {
        KeyWait,% keyname
    } else {
        KeyWait,% keyname,% options
    }
    ret := ErrorLevel

    if (ret = 1) {
        return FormatResponse("ahk.message.BooleanResponseMessage", 0)
    } else if (ret = 0) {
        return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    } else {
        ; Unclear if this is even reachable
        return FormatResponse("ahk.message.ExceptionResponseMessage", Format("There was a problem. ErrorLevel: {}", ret))
    }

    {% endblock AHKKeyWait %}
}

SetKeyDelay(args*) {
    {% block SetKeyDelay %}
    SetKeyDelay, args[1], args[2]
    {% endblock SetKeyDelay %}
}

AHKSend(args*) {
    {% block AHKSend %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
    send_mode := args[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)
    current_send_mode := Format("{}", A_SendMode)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%
    }

    if (send_mode != "") {
        SendMode, %send_mode%
    }

    Send,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }

   if (send_mode != "") {
        SendMode, %current_send_mode%
    }

    return FormatNoValueResponse()
    {% endblock AHKSend %}
}

AHKSendRaw(args*) {
    {% block AHKSendRaw %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
    send_mode := args[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)
    current_send_mode := Format("{}", A_SendMode)


    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %key_delay%, %key_press_duration%
    }

    if (send_mode != "") {
        SendMode, %send_mode%
    }

    SendRaw,% str

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay, %current_delay%, %current_key_duration%
    }

    if (send_mode != "") {
        SendMode, %current_send_mode%
    }

    return FormatNoValueResponse()
    {% endblock AHKSendRaw %}
}

AHKSendInput(args*) {
    {% block AHKSendInput %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
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

AHKSendEvent(args*) {
    {% block AHKSendEvent %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
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

AHKSendPlay(args*) {
    {% block AHKSendPlay %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
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

AHKSetCapsLockState(args*) {
    {% block AHKSetCapsLockState %}
    state := args[1]
    if (state = "") {
        SetCapsLockState % !GetKeyState("CapsLock", "T")
    } else {
        SetCapsLockState, %state%
    }
    return FormatNoValueResponse()
    {% endblock AHKSetCapsLockState %}
}


AHKSetNumLockState(args*) {
    {% block AHKSetNumLockState %}
    state := args[1]
    if (state = "") {
        SetNumLockState % !GetKeyState("NumLock", "T")
    } else {
        SetNumLockState, %state%
    }
    return FormatNoValueResponse()
    {% endblock AHKSetNumLockState %}
}

AHKSetScrollLockState(args*) {
    {% block AHKSetScrollLockState %}
    state := args[1]
    if (state = "") {
        SetScrollLockState % !GetKeyState("ScrollLock", "T")
    } else {
        SetScrollLockState, %state%
    }
    return FormatNoValueResponse()
    {% endblock AHKSetScrollLockState %}
}

HideTrayTip(args*) {
    {% block HideTrayTip %}
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        Menu Tray, NoIcon
        Sleep 200 ; It may be necessary to adjust this sleep.
        Menu Tray, Icon
    }
    {% endblock HideTrayTip %}
}

AHKWinGetClass(args*) {
    {% block AHKWinGetClass %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
        response := FormatResponse("ahk.message.ExceptionResponseMessage", "There was an error getting window class")
    } else {
        response := FormatResponse("ahk.message.StringResponseMessage", output)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return response
    {% endblock AHKWinGetClass %}
}

AHKWinActivate(args*) {
    {% block AHKWinActivate %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

AHKWindowList(args*) {
    {% block AHKWindowList %}

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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
    resp := FormatResponse("ahk.message.WindowListResponseMessage", r)
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%
    return resp
    {% endblock AHKWindowList %}
}

AHKControlClick(args*) {
    {% block AHKControlClick %}

    ctrl := args[1]
    title := args[2]
    text := args[3]
    button := args[4]
    click_count := args[5]
    options := args[6]
    exclude_title := args[7]
    exclude_text := args[8]
    detect_hw := args[9]
    match_mode := args[10]
    match_speed := args[11]

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
        response := FormatResponse("ahk.message.ExceptionResponseMessage", "Failed to click control")
    } else {
        response := FormatNoValueResponse()
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response
    {% endblock AHKControlClick %}
}

AHKControlGetText(args*) {
    {% block AHKControlGetText %}

    ctrl := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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
        response := FormatResponse("ahk.message.ExceptionResponseMessage", "There was a problem getting the text")
    } else {
        response := FormatResponse("ahk.message.StringResponseMessage", result)
    }
    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response
    {% endblock AHKControlGetText %}
}

AHKControlGetPos(args*) {
    {% block AHKControlGetPos %}

    ctrl := args[1]
    title := args[2]
    text := args[3]
    extitle := args[4]
    extext := args[5]
    detect_hw := args[6]
    match_mode := args[7]
    match_speed := args[8]

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
        response := FormatResponse("ahk.message.ExceptionResponseMessage", "There was a problem getting the text")
    } else {
        result := Format("({1:i}, {2:i}, {3:i}, {4:i})", x, y, w, h)
        response := FormatResponse("ahk.message.PositionResponseMessage", result)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response

    {% endblock AHKControlGetPos %}
}

AHKControlSend(args*) {
    {% block AHKControlSend %}
    ctrl := args[1]
    keys := args[2]
    title := args[3]
    text := args[4]
    extitle := args[5]
    extext := args[6]
    detect_hw := args[7]
    match_mode := args[8]
    match_speed := args[9]

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

AHKWinFromMouse(args*) {
    {% block AHKWinFromMouse %}

    MouseGetPos,,, MouseWin

    if (MouseWin = "") {
        return FormatNoValueResponse()
    }

    return FormatResponse("ahk.message.WindowResponseMessage", MouseWin)
    {% endblock AHKWinFromMouse %}
}

AHKWinIsAlwaysOnTop(args*) {
    {% block AHKWinIsAlwaysOnTop %}

    title := args[1]
    WinGet, ExStyle, ExStyle, %title%
    if (ExStyle = "")
        return FormatNoValueResponse()

    if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
        return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    else
        return FormatResponse("ahk.message.BooleanResponseMessage", 0)
    {% endblock AHKWinIsAlwaysOnTop %}
}

AHKWinMove(args*) {
    {% block AHKWinMove %}
    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]
    x := args[8]
    y := args[9]
    width := args[10]
    height := args[11]

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

AHKWinGetPos(args*) {
    {% block AHKWinGetPos %}

    title := args[1]
    text := args[2]
    extitle := args[3]
    extext := args[4]
    detect_hw := args[5]
    match_mode := args[6]
    match_speed := args[7]

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

    if (x = "") {
        response := FormatNoValueResponse()
    } else {
        result := Format("({1:i}, {2:i}, {3:i}, {4:i})", x, y, w, h)
        response := FormatResponse("ahk.message.PositionResponseMessage", result)
    }

    DetectHiddenWindows, %current_detect_hw%
    SetTitleMatchMode, %current_match_mode%
    SetTitleMatchMode, %current_match_speed%

    return response
    {% endblock AHKWinGetPos %}
}

AHKGetVolume(args*) {
    {% block AHKGetVolume %}

    device_number := args[1]

    try {
    SoundGetWaveVolume, retval, %device_number%
    } catch e {
        response := FormatResponse("ahk.message.ExceptionResponseMessage", Format("There was a problem getting the volume with device of index {} ({})", device_number, e.message))
        return response
    }
    if (ErrorLevel = 1) {
        response := FormatResponse("ahk.message.ExceptionResponseMessage", Format("There was a problem getting the volume with device of index {}", device_number))
    } else {
        response := FormatResponse("ahk.message.FloatResponseMessage", Format("{}", retval))
    }
    return response
    {% endblock AHKGetVolume %}
}

AHKSoundBeep(args*) {
    {% block AHKSoundBeep %}
    freq := args[1]
    duration := args[2]
    SoundBeep , %freq%, %duration%
    return FormatNoValueResponse()
    {% endblock AHKSoundBeep %}
}

AHKSoundGet(args*) {
    {% block AHKSoundGet %}

    device_number := args[1]
    component_type := args[2]
    control_type := args[3]

    SoundGet, retval, %component_type%, %control_type%, %device_number%
    ; TODO interpret return type
    return FormatResponse("ahk.message.StringResponseMessage", Format("{}", retval))
    {% endblock AHKSoundGet %}
}

AHKSoundSet(args*) {
    {% block AHKSoundSet %}
    device_number := args[1]
    component_type := args[2]
    control_type := args[3]
    value := args[4]
    SoundSet, %value%, %component_type%, %control_type%, %device_number%
    return FormatNoValueResponse()
    {% endblock AHKSoundSet %}
}

AHKSoundPlay(args*) {
    {% block AHKSoundPlay %}
    filename := args[1]
    SoundPlay, %filename%
    return FormatNoValueResponse()
    {% endblock AHKSoundPlay %}
}

AHKSetVolume(args*) {
    {% block AHKSetVolume %}
    device_number := args[1]
    value := args[2]
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

AHKEcho(args*) {
    {% block AHKEcho %}
    arg := args[1]
    return FormatResponse("ahk.message.StringResponseMessage", arg)
    {% endblock AHKEcho %}
}

AHKTraytip(args*) {
    {% block AHKTraytip %}
    title := args[1]
    text := args[2]
    second := args[3]
    option := args[4]

    TrayTip, %title%, %text%, %second%, %option%
    return FormatNoValueResponse()
    {% endblock AHKTraytip %}
}

AHKShowToolTip(args*) {
    {% block AHKShowToolTip %}
    text := args[1]
    x := args[2]
    y := args[3]
    which := args[4]
    ToolTip, %text%, %x%, %y%, %which%
    return FormatNoValueResponse()
    {% endblock AHKShowToolTip %}
}

AHKGetClipboard(args*) {
    {% block AHKGetClipboard %}

    return FormatResponse("ahk.message.StringResponseMessage", Clipboard)
    {% endblock AHKGetClipboard %}
}

AHKGetClipboardAll(args*) {
    {% block AHKGetClipboardAll %}
    data := ClipboardAll
    return FormatBinaryResponse(data)
    {% endblock AHKGetClipboardAll %}
}

AHKSetClipboard(args*) {
    {% block AHKSetClipboard %}
    text := args[1]
    Clipboard := text
    return FormatNoValueResponse()
    {% endblock AHKSetClipboard %}
}

AHKSetClipboardAll(args*) {
    {% block AHKSetClipboardAll %}
    ; TODO there should be a way for us to accept a base64 string instead
    filename := args[1]
    FileRead, Clipboard, %filename%
    return FormatNoValueResponse()
    {% endblock AHKSetClipboardAll %}
}

AHKClipWait(args*) {

    timeout := args[1]
    wait_for_any_data := args[2]

    ClipWait, %timeout%, %wait_for_any_data%

    if (ErrorLevel = 1) {
        return FormatResponse("ahk.message.TimeoutResponseMessage", "timed out waiting for clipboard data")
    }
    return FormatNoValueResponse()
}

AHKBlockInput(args*) {
    value := args[1]
    BlockInput, %value%
    return FormatNoValueResponse()
}

AHKMenuTrayTip(args*) {
    value := args[1]
    Menu, Tray, Tip, %value%
    return FormatNoValueResponse()
}

AHKMenuTrayShow(args*) {
    Menu, Tray, Icon
    return FormatNoValueResponse()
}

AHKMenuTrayHide(args*) {
    Menu, Tray, NoIcon
    return FormatNoValueResponse()
}

AHKMenuTrayIcon(args*) {
    filename := args[1]
    icon_number := args[2]
    freeze := args[3]
    Menu, Tray, Icon, %filename%, %icon_number%,%freeze%
    return FormatNoValueResponse()
}

AHKGuiNew(args*) {

    options := args[1]
    title := args[2]
    Gui, New, %options%, %title%
    return FormatResponse("ahk.message.StringResponseMessage", hwnd)
}

AHKMsgBox(args*) {

    options := args[1]
    title := args[2]
    text := args[3]
    timeout := args[4]
    MsgBox,% options, %title%, %text%, %timeout%
    IfMsgBox, Yes
        ret := FormatResponse("ahk.message.StringResponseMessage", "Yes")
    IfMsgBox, No
        ret := FormatResponse("ahk.message.StringResponseMessage", "No")
    IfMsgBox, OK
        ret := FormatResponse("ahk.message.StringResponseMessage", "OK")
    IfMsgBox, Cancel
        ret := FormatResponse("ahk.message.StringResponseMessage", "Cancel")
    IfMsgBox, Abort
        ret := FormatResponse("ahk.message.StringResponseMessage", "Abort")
    IfMsgBox, Ignore
        ret := FormatResponse("ahk.message.StringResponseMessage", "Ignore")
    IfMsgBox, Retry
        ret := FormatResponse("ahk.message.StringResponseMessage", "Retry")
    IfMsgBox, Continue
        ret := FormatResponse("ahk.message.StringResponseMessage", "Continue")
    IfMsgBox, TryAgain
        ret := FormatResponse("ahk.message.StringResponseMessage", "TryAgain")
    IfMsgBox, Timeout
        ret := FormatResponse("ahk.message.TimeoutResponseMessage", "MsgBox timed out")
    return ret
}

AHKInputBox(args*) {

    title := args[1]
    prompt := args[2]
    hide := args[3]
    width := args[4]
    height := args[5]
    x := args[6]
    y := args[7]
    locale := args[8]
    timeout := args[9]
    default := args[10]

    InputBox, output, %title%, %prompt%, %hide%, %width%, %height%, %x%, %y%, %locale%, %timeout%, %default%
    if (ErrorLevel = 2) {
        ret := FormatResponse("ahk.message.TimeoutResponseMessage", "Input box timed out")
    } else if (ErrorLevel = 1) {
        ret := FormatNoValueResponse()
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    return ret
}

AHKFileSelectFile(byRef args) {

    options := args[1]
    root := args[2]
    title := args[3]
    filter := args[4]
    FileSelectFile, output, %options%, %root%, %title%, %filter%
    if (ErrorLevel = 1) {
        ret := FormatNoValueResponse()
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    return ret
}

AHKFileSelectFolder(byRef args) {

    starting_folder := args[1]
    options := args[2]
    prompt := args[3]

    FileSelectFolder, output, %starting_folder%, %options%, %prompt%

    if (ErrorLevel = 1) {
        ret := FormatNoValueResponse()
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    return ret
}

Crypt32 := DllCall("LoadLibrary", "Str", "Crypt32.dll", "Ptr")


b64decode(ByRef pszString) {
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
    success := DllCall("Crypt32\CryptStringToBinary", "Ptr", &pszString, "UInt", cchString, "UInt", dwFlags, "UInt", getsize, "UIntP", buff_size, "Int", pdwSkip, "Int", pdwFlags)
    if (success = 0) {
        return ""
    }

    ; We're going to give a pointer to a variable to the next call, but first we want to make the buffer the correct size using VarSetCapacity using the previous return value
    VarSetCapacity(ret, buff_size, 0)

    ; Now that we know the buffer size we need and have the variable's capacity set to the proper size, we'll pass a pointer to the variable for the decoded value to be written to

    success := DllCall("Crypt32\CryptStringToBinary", "Ptr", &pszString, "UInt", cchString, "UInt", dwFlags, "Ptr", &ret, "UIntP", buff_size, "Int", pdwSkip, "Int", pdwFlags)
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

    success := DllCall("Crypt32\CryptBinaryToString", "Ptr", &data, "UInt", cbBinary, "UInt", dwFlags, "Str", ret, "UIntP", buff_size)
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

; BEGIN extension scripts
{% for ext in extensions %}
{{ ext.script_text }}

{% endfor %}
; END extension scripts

{% block before_autoexecute %}
{% endblock before_autoexecute %}

{% block autoexecute %}
stdin  := FileOpen("*", "r `n", "UTF-8")  ; Requires [v1.1.17+]
pyresp := ""

Loop {
    query := RTrim(stdin.ReadLine(), "`n")
    if (query = "") {
        ; Technically this should only happen if the Python process has died, so sending a message is probably futile
        ; But if this somehow triggers in some other case, we'll try to have an informative error raised.
        pyresp := FormatResponse("ahk.message.ExceptionResponseMessage", "Unexpected empty message; AHK exiting. This is likely a bug. Please report this issue at https://github.com/spyoungtech/ahk/issues")
        FileAppend, %pyresp%, *, UTF-8

        ; Exit to avoid leaving the process hanging around needlessly
        ExitApp
    }
    argsArray := CommandArrayFromQuery(query)
    try {
        func := argsArray[1]
        argsArray.RemoveAt(1)
        {% block before_function %}
        {% endblock before_function %}
        pyresp := %func%(argsArray*)
        {% block after_function %}
        {% endblock after_function %}
    } catch e {
        {% block function_error_handle %}
        message := Format("Error occurred in {}. The error message was: {}", e.What, e.message)
        pyresp := FormatResponse("ahk.message.ExceptionResponseMessage", message)
        {% endblock function_error_handle %}
    }
    {% block send_response %}
    if (pyresp) {
        FileAppend, %pyresp%, *, UTF-8
    } else {
        msg := FormatResponse("ahk.message.ExceptionResponseMessage", Format("Unknown Error when calling {}", func))
        FileAppend, %msg%, *, UTF-8
    }
    {% endblock send_response %}
}
{% endblock autoexecute %}
{% endblock daemon_script %}
