{% block daemon_script %}
{% block directives %}
;#NoEnv
;#Persistent
#Requires Autohotkey >= 2.0-
#Warn All, Off
#SingleInstance Off
; BEGIN user-defined directives
{% block user_directives %}
{% for directive in directives %}
{{ directive }}

{% endfor %}

; END user-defined directives
{% endblock user_directives %}
{% endblock directives %}

Critical 100


{% block message_types %}
MESSAGE_TYPES := Map({% for tom, msg_class in message_registry.items() %}"{{ msg_class.fqn() }}", "{{ tom.decode('utf-8') }}"{% if not loop.last %}, {% endif %}{% endfor %})
{% endblock message_types %}

NOVALUE_SENTINEL := Chr(57344)

StrCount(haystack, needle) {
    StrReplace(haystack, needle, "",, &count)
    return count
}

FormatResponse(MessageType, payload) {
    global MESSAGE_TYPES
    newline_count := StrCount(payload, "`n")
    response := Format("{}`n{}`n{}`n", MESSAGE_TYPES[MessageType], newline_count, payload)
    return response
}

FormatNoValueResponse() {
    global NOVALUE_SENTINEL
    return FormatResponse("ahk.message.NoValueResponseMessage", NOVALUE_SENTINEL)
}

FormatBinaryResponse(bin) {
    b64 := b64encode(bin)
    return FormatResponse("ahk.message.B64BinaryResponseMessage", b64)
}

AHKSetDetectHiddenWindows(command) {
    {% block AHKSetDetectHiddenWindows %}
    value := command[2]
    DetectHiddenWindows(value)
    return FormatNoValueResponse()
    {% endblock AHKSetDetectHiddenWindows %}
}

AHKSetTitleMatchMode(command) {
    {% block AHKSetTitleMatchMode %}
    val1 := command[2]
    val2 := command[3]
    if (val1 != "") {
        SetTitleMatchMode(val1)
    }
    if (val2 != "") {
        SetTitleMatchMode(val2)
    }
    return FormatNoValueResponse()
    {% endblock AHKSetTitleMatchMode %}
}

AHKGetTitleMatchMode(command) {
    {% block AHKGetTitleMatchMode %}

    return FormatResponse("ahk.message.StringResponseMessage", A_TitleMatchMode)
    {% endblock AHKGetTitleMatchMode %}
}

AHKGetTitleMatchSpeed(command) {
    {% block AHKGetTitleMatchSpeed %}

    return FormatResponse("ahk.message.StringResponseMessage", A_TitleMatchModeSpeed)
    {% endblock AHKGetTitleMatchSpeed %}
}

AHKSetSendLevel(command) {
    {% block AHKSetSendLevel %}
    level := command[2]
    SendLevel(level)
    return FormatNoValueResponse()
    {% endblock AHKSetSendLevel %}
}

AHKGetSendLevel(command) {
    {% block AHKGetSendLevel %}

    return FormatResponse("ahk.message.IntegerResponseMessage", A_SendLevel)
    {% endblock AHKGetSendLevel %}
}

AHKWinExist(command) {
    {% block AHKWinExist %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    if WinExist(title, text, extitle, extext) {
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 1)
    } else {
        resp := FormatResponse("ahk.message.BooleanResponseMessage", 0)
    }

    DetectHiddenWindows(current_detect_hw)
    SetTitleMatchMode(current_match_mode)
    SetTitleMatchMode(current_match_speed)

    return resp
    {% endblock AHKWinExist %}
}

AHKWinClose(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    WinClose(title, text, secondstowait, extitle, extext)

    DetectHiddenWindows(current_detect_hw)
    SetTitleMatchMode(current_match_mode)
    SetTitleMatchMode(current_match_speed)

    return FormatNoValueResponse()
    {% endblock AHKWinClose %}
}

AHKWinKill(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    WinKill(title, text, secondstowait, extitle, extext)

    DetectHiddenWindows(current_detect_hw)
    SetTitleMatchMode(current_match_mode)
    SetTitleMatchMode(current_match_speed)

    return FormatNoValueResponse()
    {% endblock AHKWinKill %}
}

AHKWinWait(command) {
    {% block AHKWinWait %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        if (timeout != "") {
            output := WinWait(title, text, timeout, extitle, extext)
            if (output = 0) {
                resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
            } else {
                resp := resp := FormatResponse("ahk.message.WindowResponseMessage", output)
            }
        } else {
            output := WinWait(title, text,, extitle, extext)
            resp := FormatResponse("ahk.message.WindowResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return resp
    {% endblock AHKWinWait %}
}

AHKWinWaitActive(command) {
    {% block AHKWinWaitActive %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        if (timeout != "") {
            output := WinWaitActive(title, text, timeout, extitle, extext)
            if (output = 0) {
                resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWaitActive timed out waiting for the window")
            } else {
                resp := FormatResponse("ahk.message.WindowResponseMessage", output)
            }
        } else {
            output := WinWaitActive(title, text,, extitle, extext)
            resp := FormatResponse("ahk.message.WindowResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return resp
    {% endblock AHKWinWaitActive %}
}

AHKWinWaitNotActive(command) {
    {% block AHKWinWaitNotActive %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        if (timeout != "") {
            if (WinWaitNotActive(title, text, timeout, extitle, extext) = 1) {
                output := WinGetID()
                resp := FormatResponse("ahk.message.WindowResponseMessage", output)
            } else {
                resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
            }
        } else {
            WinWaitNotActive(title, text,, extitle, extext)
            output := WinGetID()
            resp := FormatResponse("ahk.message.WindowResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return resp
    {% endblock AHKWinWaitNotActive %}
}

AHKWinWaitClose(command) {
    {% block AHKWinWaitClose %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        if (timeout != "") {
            if (WinWaitClose(title, text, timeout, extitle, extext) = 1) {
                resp := FormatNoValueResponse()
            } else {
                resp := FormatResponse("ahk.message.TimeoutResponseMessage", "WinWait timed out waiting for window")
            }
        } else {
            WinWaitClose(title, text,, extitle, extext)
            resp := FormatNoValueResponse()
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return resp
    {% endblock AHKWinWaitClose %}
}

AHKWinMinimize(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinMinimize(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinMinimize %}
}

AHKWinMaximize(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    WinMaximize(title, text, extitle, extext)

    DetectHiddenWindows(current_detect_hw)
    SetTitleMatchMode(current_match_mode)
    SetTitleMatchMode(current_match_speed)

    return FormatNoValueResponse()
    {% endblock AHKWinMaximize %}
}

AHKWinRestore(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinRestore(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinRestore %}
}

AHKWinIsActive(command) {
    {% block AHKWinIsActive %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        if WinActive(title, text, extitle, extext) {
            response := FormatResponse("ahk.message.BooleanResponseMessage", 1)
        } else {
            response := FormatResponse("ahk.message.BooleanResponseMessage", 0)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinIsActive %}
}

AHKWinGetID(command) {
    {% block AHKWinGetID %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetID(title, text, extitle, extext)
        if (output = 0 || output = "") {
            response := FormatNoValueResponse()
        } else {
            response := FormatResponse("ahk.message.WindowResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetID %}
}

AHKWinGetTitle(command) {
    {% block AHKWinGetTitle %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        text := WinGetTitle(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatResponse("ahk.message.StringResponseMessage", text)
    {% endblock AHKWinGetTitle %}
}

AHKWinGetIDLast(command) {
    {% block AHKWinGetIDLast %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        output := WinGetIDLast(title, text, extitle, extext)
        if (output = 0 || output = "") {
            response := FormatNoValueResponse()
        } else {
            response := FormatResponse("ahk.message.WindowResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetIDLast %}
}

AHKWinGetPID(command) {
    {% block AHKWinGetPID %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetPID(title, text, extitle, extext)
        if (output = 0 || output = "") {
            response := FormatNoValueResponse()
        } else {
            response := FormatResponse("ahk.message.IntegerResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetPID %}
}

AHKWinGetProcessName(command) {
    {% block AHKWinGetProcessName %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        output := WinGetProcessName(title, text, extitle, extext)
        if (output = 0 || output = "") {
            response := FormatNoValueResponse()
        } else {
            response := FormatResponse("ahk.message.StringResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetProcessName %}
}

AHKWinGetProcessPath(command) {
    {% block AHKWinGetProcessPath %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetProcessPath(title, text, extitle, extext)
        if (output = 0 || output = "") {
            response := FormatNoValueResponse()
        } else {
            response := FormatResponse("ahk.message.StringResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetProcessPath %}
}

AHKWinGetCount(command) {
    {% block AHKWinGetCount %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        output := WinGetCount(title, text, extitle, extext)
        if (output = 0) {
            response := FormatResponse("ahk.message.IntegerResponseMessage", output)
        } else {
            response := FormatResponse("ahk.message.IntegerResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetCount %}
}

AHKWinGetMinMax(command) {
    {% block AHKWinGetMinMax %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        output := WinGetMinMax(title, text, extitle, extext)
        if (output = "") {
            response := FormatNoValueResponse()
        } else {
            response := FormatResponse("ahk.message.IntegerResponseMessage", output)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetMinMax %}
}

AHKWinGetControlList(command) {
    {% block AHKWinGetControlList %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    ahkid := WinGetID(title, text, extitle, extext)

    if (ahkid = "") {
        return FormatNoValueResponse()
    }

    try {
        ctrList := WinGetControls(title, text, extitle, extext)
        ctrListID := WinGetControlsHwnd(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    if (ctrListID = "") {
        return FormatResponse("ahk.message.WindowControlListResponseMessage", Format("('{}', [])", ahkid))
    }

    ; ctrListArr := StrSplit(ctrList, "`n")
    ; ctrListIDArr := StrSplit(ctrListID, "`n")
    if (ctrListArr.Length() != ctrListIDArr.Length()) {
        return FormatResponse("ahk.message.ExceptionResponseMessage", "Control hwnd/class lists have unexpected lengths")
    }

    output := Format("('{}', [", ahkid)

    for index, hwnd in ctrListIDArr {
        classname := ctrListArr[index]
        output .= Format("('{}', '{}'), ", hwnd, classname)

    }
    output .= "])"
    response := FormatResponse("ahk.message.WindowControlListResponseMessage", output)
    return response
    {% endblock AHKWinGetControlList %}
}

AHKWinGetTransparent(command) {
    {% block AHKWinGetTransparent %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetTransparent(title, text, extitle, extext)
        response := FormatResponse("ahk.message.IntegerResponseMessage", output)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetTransparent %}
}
AHKWinGetTransColor(command) {
    {% block AHKWinGetTransColor %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetTransColor(title, text, extitle, extext)
        response := FormatResponse("ahk.message.NoValueResponseMessage", output)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetTransColor %}
}
AHKWinGetStyle(command) {
    {% block AHKWinGetStyle %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        output := WinGetStyle(title, text, extitle, extext)
        response := FormatResponse("ahk.message.NoValueResponseMessage", output)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetStyle %}
}

AHKWinGetExStyle(command) {
    {% block AHKWinGetExStyle %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetExStyle(title, text, extitle, extext)
        response := FormatResponse("ahk.message.NoValueResponseMessage", output)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKWinGetExStyle %}
}

AHKWinGetText(command) {
    {% block AHKWinGetText %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        output := WinGetText(title,text,extitle,extext)
        response := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }

    return response
    {% endblock AHKWinGetText %}
}

AHKWinSetTitle(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetTitle(title, text, new_title, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetTitle %}
}

AHKWinSetAlwaysOnTop(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetAlwaysOnTop(toggle, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetAlwaysOnTop %}
}

AHKWinSetBottom(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinMoveBottom(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetBottom %}
}

AHKWinShow(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinShow(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinShow %}
}

AHKWinHide(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinHide(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinHide %}
}

AHKWinSetTop(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinMoveTop(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetTop %}
}

AHKWinSetEnable(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetEnabled(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetEnable %}
}

AHKWinSetDisable(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetDisabled(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetDisable %}
}

AHKWinSetRedraw(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinRedraw(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetRedraw %}
}

AHKWinSetStyle(command) {
    {% block AHKWinSetStyle %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetStyle(style, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    {% endblock AHKWinSetStyle %}
}

AHKWinSetExStyle(command) {
    {% block AHKWinSetExStyle %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        WinSetExStyle(style, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    {% endblock AHKWinSetExStyle %}
}

AHKWinSetRegion(command) {
    {% block AHKWinSetRegion %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetRegion(options, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    {% endblock AHKWinSetRegion %}
}

AHKWinSetTransparent(command) {
    {% block AHKWinSetTransparent %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetTransparent(transparency, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetTransparent %}
}

AHKWinSetTransColor(command) {
    {% block AHKWinSetTransColor %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        WinSetTransColor(color, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinSetTransColor %}
}

AHKImageSearch(command) {
    {% block AHKImageSearch %}

    imagepath := command[6]
    x1 := command[2]
    y1 := command[3]
    x2 := command[4]
    y2 := command[5]
    coord_mode := command[7]

    current_mode := Format("{}", A_CoordModePixel)

    if (coord_mode != "") {
        CoordMode(Pixel, coord_mode)
    }

    if (x2 = "A_ScreenWidth") {
        x2 := A_ScreenWidth
    }
    if (y2 = "A_ScreenHeight") {
        y2 := A_ScreenHeight
    }

    try {
        if ImageSearch(&xpos, &ypos, x1, y1, x2, y2, imagepath)
            s := FormatResponse("ahk.message.CoordinateResponseMessage", Format("({}, {})", xpos, ypos))
        else
            s := FormatNoValueResponse()
    }
    finally {
        if (coord_mode != "") {
            CoordMode(Pixel, current_mode)
        }
    }

    return s
    {% endblock AHKImageSearch %}
}

AHKPixelGetColor(command) {
    {% block AHKPixelGetColor %}

    x := command[2]
    y := command[3]
    coord_mode := command[4]
    options := command[5]

    current_mode := Format("{}", A_CoordModePixel)

    if (coord_mode != "") {
        CoordMode(Pixel, coord_mode)
    }

    try {
        color := PixelGetColor(x, y, options)
    }
    finally {
        if (coord_mode != "") {
            CoordMode(Pixel, current_mode)
        }
    }

    return FormatResponse("ahk.message.StringResponseMessage", color)
    {% endblock AHKPixelGetColor %}
}

AHKPixelSearch(command) {
    {% block AHKPixelSearch %}

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
        CoordMode(Pixel, coord_mode)
    }
    try {
        if (PixelSearch(&resultx, &resulty, x1, y1, x2, y2, color, variation) = 1) {
            payload := Format("({}, {})", resultx, resulty)
            ret := FormatResponse("ahk.message.CoordinateResponseMessage", payload)
        } else {
            ret := FormatNoValueResponse()
        }
    }
    finally {
        if (coord_mode != "") {
            CoordMode(Pixel, current_mode)
        }
    }

    return ret

    {% endblock AHKPixelSearch %}
}

AHKMouseGetPos(command) {
    {% block AHKMouseGetPos %}

    coord_mode := command[2]
    current_coord_mode := Format("{}", A_CoordModeMouse)
    if (coord_mode != "") {
        CoordMode(Mouse, coord_mode)
    }
    MouseGetPos(&xpos, &ypos)

    payload := Format("({}, {})", xpos, ypos)
    resp := FormatResponse("ahk.message.CoordinateResponseMessage", payload)

    if (coord_mode != "") {
        CoordMode(Mouse, current_coord_mode)
    }

    return resp
    {% endblock AHKMouseGetPos %}
}

AHKKeyState(command) {
    {% block AHKKeyState %}

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

    if IsInteger(state)
        return FormatResponse("ahk.message.IntegerResponseMessage", state)

    if IsFloat(state)
        return FormatResponse("ahk.message.FloatResponseMessage", state)

    if IsAlnum(state)
        return FormatResponse("ahk.message.StringResponseMessage", state)

    msg := Format("Unexpected key state {}", state)
    return FormatResponse("ahk.message.ExceptionResponseMessage", msg)
    {% endblock AHKKeyState %}
}

AHKMouseMove(command) {
    {% block AHKMouseMove %}
    x := command[2]
    y := command[3]
    speed := command[4]
    relative := command[5]
    if (relative != "") {
    MouseMove(x, y, speed, "R")
    } else {
    MouseMove(x, y, speed)
    }
    resp := FormatNoValueResponse()
    return resp
    {% endblock AHKMouseMove %}
}

AHKClick(command) {
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
        CoordMode(Mouse, relative_to)
    }

    Click(x, y, button, direction, r)

    if (relative_to != "") {
        CoordMode(Mouse, current_coord_rel)
    }

    return FormatNoValueResponse()

    {% endblock AHKClick %}
}

AHKGetCoordMode(command) {
    {% block AHKGetCoordMode %}

    target := command[2]

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

AHKSetCoordMode(command) {
    {% block AHKSetCoordMode %}
    target := command[2]
    relative_to := command[3]
    CoordMode(target, relative_to)

    return FormatNoValueResponse()
    {% endblock AHKSetCoordMode %}
}

AHKMouseClickDrag(command) {
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
        CoordMode(Mouse, relative_to)
    }

    MouseClickDrag(button, x1, y1, x2, y2, speed, relative)

    if (relative_to != "") {
        CoordMode(Mouse, current_coord_rel)
    }

    return FormatNoValueResponse()

    {% endblock AHKMouseClickDrag %}
}

AHKRegRead(command) {
    {% block RegRead %}

    key_name := command[2]
    value_name := command[3]

    output := RegRead(key_name, value_name)
    resp := FormatResponse("ahk.message.StringResponseMessage", Format("{}", output))
    return resp
    {% endblock RegRead %}
}

AHKRegWrite(command) {
    {% block RegWrite %}
    value_type := command[2]
    key_name := command[3]
    value_name := command[4]
    value := command[5]
;    RegWrite(value_type, key_name, value_name, value)
    if (value_name != "") {
        RegWrite(value, value_type, key_name)
    } else {
        RegWrite(value, value_type, key_name, value_name)
    }
    return FormatNoValueResponse()
    {% endblock RegWrite %}
}

AHKRegDelete(command) {
    {% block RegDelete %}

    key_name := command[2]
    value_name := command[3]
    if (value_name != "") {
        RegDelete(key_name, value_name)
    } else {
        RegDelete(key_name)
    }
    return FormatNoValueResponse()

    {% endblock RegDelete %}
}

AHKKeyWait(command) {
    {% block AHKKeyWait %}

    keyname := command[2]
    if (command.Length() = 2) {
        ret := KeyWait(keyname)
    } else {
        options := command[3]
        ret := KeyWait(keyname, options)
    }
    return FormatResponse("ahk.message.IntegerResponseMessage", ret)
    {% endblock AHKKeyWait %}
}

;SetKeyDelay(command) {
;    {% block SetKeyDelay %}
;    SetKeyDelay(command[2], command[3])
;    {% endblock SetKeyDelay %}
;}

AHKSend(command) {
    {% block AHKSend %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(key_delay, key_press_duration)
    }


    Send(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSend %}
}

AHKSendRaw(command) {
    {% block AHKSendRaw %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(key_delay, key_press_duration)
    }

    SendRaw(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSendRaw %}
}

AHKSendInput(command) {
    {% block AHKSendInput %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(key_delay, key_press_duration)
    }

    SendInput(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSendInput %}
}

AHKSendEvent(command) {
    {% block AHKSendEvent %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(key_delay, key_press_duration)
    }

    SendEvent(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSendEvent %}
}

AHKSendPlay(command) {
    {% block AHKSendPlay %}
    str := command[2]
    key_delay := command[3]
    key_press_duration := command[4]
    current_delay := Format("{}", A_KeyDelayPlay)
    current_key_duration := Format("{}", A_KeyDurationPlay)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(key_delay, key_press_duration, Play)
    }

    SendPlay(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSendPlay %}
}

AHKSetCapsLockState(command) {
    {% block AHKSetCapsLockState %}
    state := command[2]
    if (state = "") {
        SetCapsLockState(!GetKeyState("CapsLock", "T"))
    } else {
        SetCapsLockState(state)
    }
    return FormatNoValueResponse()
    {% endblock AHKSetCapsLockState %}
}

HideTrayTip(command) {
    {% block HideTrayTip %}
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        Menu Tray, NoIcon
        Sleep 200 ; It may be necessary to adjust this sleep.
        Menu Tray, Icon
    }
    {% endblock HideTrayTip %}
}

AHKWinGetClass(command) {
    {% block AHKWinGetClass %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    try {
        output := WinGetClass(title,text,extitle,extext)
        response := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }

    return response
    {% endblock AHKWinGetClass %}
}

AHKWinActivate(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }

    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        WinActivate(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKWinActivate %}
}

AHKWindowList(command) {
    {% block AHKWindowList %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    if (detect_hw) {
        DetectHiddenWindows(detect_hw)
    }
    try {
        windows := WinGetList(title, text, extitle, extext)
        r := ""
        for id in windows
        {
            r .= id . "`,"
        }
        resp := FormatResponse("ahk.message.WindowListResponseMessage", r)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return resp
    {% endblock AHKWindowList %}
}

AHKControlClick(command) {
    {% block AHKControlClick %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        ControlClick(ctrl, title, text, button, click_count, options, exclude_title, exclude_text)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    response := FormatNoValueResponse()
    return response
    {% endblock AHKControlClick %}
}

AHKControlGetText(command) {
    {% block AHKControlGetText %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        result := ControlGetText(ctrl, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    response := FormatResponse("ahk.message.StringResponseMessage", result)

    return response
    {% endblock AHKControlGetText %}
}

AHKControlGetPos(command) {
    {% block AHKControlGetPos %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        ControlGetPos(&x, &y, &w, &h, ctrl, title, text, extitle, extext)
        result := Format("({1:i}, {2:i}, {3:i}, {4:i})", x, y, w, h)
        response := FormatResponse("ahk.message.PositionResponseMessage", result)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return response
    {% endblock AHKControlGetPos %}
}

AHKControlSend(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        ControlSend(ctrl, keys, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKControlSend %}
}

AHKWinFromMouse(command) {
    {% block AHKWinFromMouse %}

    MouseGetPos(,, MouseWin)

    if (MouseWin = "") {
        return FormatNoValueResponse()
    }

    return FormatResponse("ahk.message.WindowResponseMessage", MouseWin)
    {% endblock AHKWinFromMouse %}
}

AHKWinIsAlwaysOnTop(command) {
    {% block AHKWinIsAlwaysOnTop %}
    ; TODO: detect hidden windows / etc?
    title := command[2]
    ExStyle := WinGetExStyle(title)
    if (ExStyle = "")
        return FormatNoValueResponse()

    if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
        return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    else
        return FormatResponse("ahk.message.BooleanResponseMessage", 0)
    {% endblock AHKWinIsAlwaysOnTop %}
}

AHKWinMove(command) {
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        WinMove(title, text, x, y, width, height, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()

    {% endblock AHKWinMove %}
}

AHKWinGetPos(command) {
    {% block AHKWinGetPos %}

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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    try {
        WinGetPos(&x, &y, &w, &h, title, text, extitle, extext)
        result := Format("({1:i}, {2:i}, {3:i}, {4:i})", x, y, w, h)
        response := FormatResponse("ahk.message.PositionResponseMessage", result)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }

    return response
    {% endblock AHKWinGetPos %}
}

AHKGetVolume(command) {
    {% block AHKGetVolume %}

    device_number := command[2]

    retval := SoundGetVolume(,device_number)
    response := FormatResponse("ahk.message.FloatResponseMessage", Format("{}", retval))
    return response
    {% endblock AHKGetVolume %}
}

AHKSoundBeep(command) {
    {% block AHKSoundBeep %}
    freq := command[2]
    duration := command[3]
    SoundBeep(freq, duration)
    return FormatNoValueResponse()
    {% endblock AHKSoundBeep %}
}

AHKSoundGet(command) {
    {% block AHKSoundGet %}
    return FormatResponse("ahk.message.ExceptionResponseMessage", "SoundGet is not supported in ahk v2")
    {% endblock AHKSoundGet %}
}

AHKSoundSet(command) {
    {% block AHKSoundSet %}
    return FormatResponse("ahk.message.ExceptionResponseMessage", "SoundSet is not supported in ahk v2")
    {% endblock AHKSoundSet %}
}

AHKSoundPlay(command) {
    {% block AHKSoundPlay %}
    filename := command[2]
    SoundPlay(filename)
    return FormatNoValueResponse()
    {% endblock AHKSoundPlay %}
}

AHKSetVolume(command) {
    {% block AHKSetVolume %}
    device_number := command[2]
    value := command[3]
    SoundSetVolume(value,,device_number)
    return FormatNoValueResponse()
    {% endblock AHKSetVolume %}
}


AHKEcho(command) {
    {% block AHKEcho %}
    arg := command[2]
    return FormatResponse("ahk.message.StringResponseMessage", arg)
    {% endblock AHKEcho %}
}

AHKTraytip(command) {
    {% block AHKTraytip %}
    title := command[2]
    text := command[3]
    second := command[4]
    option := command[5]

    TrayTip(title, text, option)
    return FormatNoValueResponse()
    {% endblock AHKTraytip %}
}

AHKShowToolTip(command) {
    {% block AHKShowToolTip %}
    text := command[2]
    x := command[3]
    y := command[4]
    which := command[5]
    ToolTip(text, x, y, which)
    return FormatNoValueResponse()
    {% endblock AHKShowToolTip %}
}

AHKGetClipboard(command) {
    {% block AHKGetClipboard %}

    return FormatResponse("ahk.message.StringResponseMessage", A_Clipboard)
    {% endblock AHKGetClipboard %}
}

AHKGetClipboardAll(command) {
    {% block AHKGetClipboardAll %}
    data := ClipboardAll()
    return FormatBinaryResponse(data)
    {% endblock AHKGetClipboardAll %}
}

AHKSetClipboard(command) {
    {% block AHKSetClipboard %}
    text := command[2]
    A_Clipboard := text
    return FormatNoValueResponse()
    {% endblock AHKSetClipboard %}
}

AHKSetClipboardAll(command) {
    {% block AHKSetClipboardAll %}
    ; TODO there should be a way for us to accept a base64 string instead
    filename := command[2]
    contents := FileRead(filename, "RAW")
    ClipboardAll(contents)
    return FormatNoValueResponse()
    {% endblock AHKSetClipboardAll %}
}

AHKClipWait(command) {

    timeout := command[2]
    wait_for_any_data := command[3]

    if ClipWait(timeout, wait_for_any_data)
        return FormatNoValueResponse()
    else
        return FormatResponse("ahk.message.TimeoutResponseMessage", "timed out waiting for clipboard data")
    return FormatNoValueResponse()
}

AHKBlockInput(command) {
    value := command[2]
    BlockInput(value)
    return FormatNoValueResponse()
}

AHKMenuTrayTip(command) {
    value := command[2]
    Menu(Tray, Tip, value)
    return FormatNoValueResponse()
}

AHKMenuTrayShow(command) {
    Menu(Tray, Icon)
    return FormatNoValueResponse()
}

AHKMenuTrayIcon(command) {
    filename := command[2]
    icon_number := command[3]
    freeze := command[4]
    Menu(Tray, Icon, filename, icon_number,freeze)
    return FormatNoValueResponse()
}

AHKGuiNew(command) {

    options := command[2]
    title := command[3]
    Gui(New, options, title)
    return FormatResponse("ahk.message.StringResponseMessage", hwnd)
}

AHKMsgBox(command) {

    options := command[2]
    title := command[3]
    text := command[4]
    timeout := command[5]
    if (timeout != "") {
        options := "" options " T" timeout
    }
    res := MsgBox(text, title, options)
    if (res = "Timeout") {
        ret := FormatResponse("ahk.message.TimeoutResponseMessage", "MsgBox timed out")
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", res)
    }
    return ret
}

AHKInputBox(command) {

    title := command[2]
    prompt := command[3]
    hide := command[4]
    width := command[5]
    height := command[6]
    x := command[7]
    y := command[8]
    locale := command[9]
    timeout := command[10]
    default := command[11]

    ; TODO: support options correctly
    options := ""
    if (timeout != "") {
        options .= "T" timeout
    }
    output := InputBox(prompt, title, options, default)
    if (output.Result = "Timeout") {
        ret := FormatResponse("ahk.message.TimeoutResponseMessage", "Input box timed out")
    } else if (output.Result = "Cancel") {
        ret := FormatNoValueResponse()
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", output.Value)
    }
    return ret
}

AHKFileSelectFile(command) {

    options := command[2]
    root := command[3]
    title := command[4]
    filter := command[5]
    output := FileSelect(options, root, title, filter)
    if (output = "") {
        ret := FormatNoValueResponse()
    } else {
        if IsObject(output) {
            if (output.Length = 0) {
                ret := FormatNoValueResponse()
            }
            else {
                files := ""
                for index, filename in output
                    if (A_Index != 1) {
                        files .= "`n"
                    }
                    files .= filename
                ret := FormatResponse("ahk.message.StringResponseMessage", files)
            }
        } else {
            ret := FormatResponse("ahk.message.StringResponseMessage", output)
        }
    }
    return ret
}

AHKFileSelectFolder(command) {

    starting_folder := command[2]
    options := command[3]
    prompt := command[4]

    output := DirSelect(starting_folder, options, prompt)

    if (output = "") {
        ret := FormatNoValueResponse()
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    return ret
}

; LC_* functions are substantially from Libcrypt
; Modified from https://github.com/ahkscript/libcrypt.ahk
; Ref: https://www.autohotkey.com/boards/viewtopic.php?t=112821
; Original License:
;    The MIT License (MIT)
;
;    Copyright (c) 2014 The ahkscript community (ahkscript.org)
;
;    Permission is hereby granted, free of charge, to any person obtaining a copy
;    of this software and associated documentation files (the "Software"), to deal
;    in the Software without restriction, including without limitation the rights
;    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
;    copies of the Software, and to permit persons to whom the Software is
;    furnished to do so, subject to the following conditions:
;
;    The above copyright notice and this permission notice shall be included in all
;    copies or substantial portions of the Software.


LC_Base64_Encode_Text(Text_, Encoding_ := "UTF-8")
{
    Bin_ := Buffer(StrPut(Text_, Encoding_))
    LC_Base64_Encode(&Base64_, &Bin_, StrPut(Text_, Bin_, Encoding_) - 1)
    return Base64_
}

LC_Base64_Decode_Text(Text_, Encoding_ := "UTF-8")
{
    Len_ := LC_Base64_Decode(&Bin_, &Text_)
    return StrGet(StrPtr(Bin_), Len_, Encoding_)
}

LC_Base64_Encode(&Out_, &In_, In_Len)
{
    return LC_Bin2Str(&Out_, &In_, In_Len, 0x40000001)
}

LC_Base64_Decode(&Out_, &In_)
{
    return LC_Str2Bin(&Out_, &In_, 0x1)
}

LC_Bin2Str(&Out_, &In_, In_Len, Flags_)
{
    DllCall("Crypt32.dll\CryptBinaryToString", "Ptr", In_, "UInt", In_Len, "UInt", Flags_, "Ptr", 0, "UInt*", &Out_Len := 0)
    VarSetStrCapacity(&Out_, Out_Len * 2)
    DllCall("Crypt32.dll\CryptBinaryToString", "Ptr", In_, "UInt", In_Len, "UInt", Flags_, "Str", Out_, "UInt*", &Out_Len)
    return Out_Len
}

LC_Str2Bin(&Out_, &In_, Flags_)
{
    DllCall("Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(In_), "UInt", StrLen(In_), "UInt", Flags_, "Ptr", 0, "UInt*", &Out_Len := 0, "Ptr", 0, "Ptr", 0)
    VarSetStrCapacity(&Out_, Out_Len)
    DllCall("Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(In_), "UInt", StrLen(In_), "UInt", Flags_, "Str", Out_, "UInt*", &Out_Len, "Ptr", 0, "Ptr", 0)
    return Out_Len
}
; End of libcrypt code

b64decode(pszString) {
    ; TODO load DLL globally for performance
    ; REF: https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptstringtobinaryw
    ;  [in]      LPCSTR pszString,  A pointer to a string that contains the formatted string to be converted.
    ;  [in]      DWORD  cchString,  The number of characters of the formatted string to be converted, not including the terminating NULL character. If this parameter is zero, pszString is considered to be a null-terminated string.
    ;  [in]      DWORD  dwFlags,    Indicates the format of the string to be converted. (see table in link above)
    ;  [in]      BYTE   *pbBinary,  A pointer to a buffer that receives the returned sequence of bytes. If this parameter is NULL, the function calculates the length of the buffer needed and returns the size, in bytes, of required memory in the DWORD pointed to by pcbBinary.
    ;  [in, out] DWORD  *pcbBinary, A pointer to a DWORD variable that, on entry, contains the size, in bytes, of the pbBinary buffer. After the function returns, this variable contains the number of bytes copied to the buffer. If this value is not large enough to contain all of the data, the function fails and GetLastError returns ERROR_MORE_DATA.
    ;  [out]     DWORD  *pdwSkip,   A pointer to a DWORD value that receives the number of characters skipped to reach the beginning of the -----BEGIN ...----- header. If no header is present, then the DWORD is set to zero. This parameter is optional and can be NULL if it is not needed.
    ;  [out]     DWORD  *pdwFlags   A pointer to a DWORD value that receives the flags actually used in the conversion. These are the same flags used for the dwFlags parameter. In many cases, these will be the same flags that were passed in the dwFlags parameter. If dwFlags contains one of the following flags, this value will receive a flag that indicates the actual format of the string. This parameter is optional and can be NULL if it is not needed.
    return LC_Base64_Decode_Text(pszString)
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
    success := DllCall("Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(pszString), "UInt", cchString, "UInt", dwFlags, "UInt", getsize, "UIntP", buff_size, "Int", pdwSkip, "Int", pdwFlags )
    if (success = 0) {
        return ""
    }

    ; We're going to give a pointer to a variable to the next call, but first we want to make the buffer the correct size using VarSetCapacity using the previous return value
    ret := Buffer(buff_size, 0)
;    granted := VarSetStrCapacity(&ret, buff_size)

    ; Now that we know the buffer size we need and have the variable's capacity set to the proper size, we'll pass a pointer to the variable for the decoded value to be written to

    success := DllCall( "Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(pszString), "UInt", cchString, "UInt", dwFlags, "Ptr", ret, "UIntP", buff_size, "Int", pdwSkip, "Int", pdwFlags )
    if (success=0) {
        return ""
    }

    return StrGet(ret, "UTF-8")
}

b64encode(data) {
    ; REF: https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptbinarytostringa
    ;  [in]            const BYTE *pbBinary: A pointer to the array of bytes to be converted into a string.
    ;  [in]            DWORD      cbBinary: The number of elements in the pbBinary array.
    ;  [in]            DWORD      dwFlags: Specifies the format of the resulting formatted string (see table in REF)
    ;  [out, optional] LPSTR      pszString: A pointer to the string, or null (0) to calculate size
    ;  [in, out]       DWORD      *pcchString: A pointer to a DWORD variable that contains the size, in TCHARs, of the pszString buffer
    LC_Base64_Encode(&Base64_, &data, data.Size)
    return Base64_
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

CommandArrayFromQuery(text) {
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
stdout := FileOpen("*", "w", "UTF-8")
pyresp := ""

Loop {
    query := RTrim(stdin.ReadLine(), "`n")
    commandArray := CommandArrayFromQuery(query)
    try {
        func_name := commandArray[1]
        {% block before_function %}
        {% endblock before_function %}
        pyresp := %func_name%(commandArray)
        {% block after_function %}
        {% endblock after_function %}
    } catch Any as e {
        {% block function_error_handle %}
        message := Format("Error occurred in {} (line {}). The error message was: {}. Specifically: {}", e.what, e.line, e.message e.extra)
        pyresp := FormatResponse("ahk.message.ExceptionResponseMessage", message)
        {% endblock function_error_handle %}
    }
    {% block send_response %}
    if (pyresp) {
        stdout.Write(pyresp)
        stdout.Read(0)
    } else {
        msg := FormatResponse("ahk.message.ExceptionResponseMessage", Format("Unknown Error when calling {}", func_name))
        stdout.Write(msg)
        stdout.Read(0)
    }
    {% endblock send_response %}
}

{% endblock autoexecute %}
{% endblock daemon_script %}
