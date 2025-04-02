{% block daemon_script %}
{% block directives %}
;#NoEnv
#Requires Autohotkey >= 2.0-
Persistent
;#Warn All, Off
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

AHKSetDetectHiddenWindows(args*) {
    {% block AHKSetDetectHiddenWindows %}
    value := args[1]
    DetectHiddenWindows(value)
    return FormatNoValueResponse()
    {% endblock AHKSetDetectHiddenWindows %}
}

AHKSetTitleMatchMode(args*) {
    {% block AHKSetTitleMatchMode %}
    val1 := args[1]
    val2 := args[2]
    if (val1 != "") {
        SetTitleMatchMode(val1)
    }
    if (val2 != "") {
        SetTitleMatchMode(val2)
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
    SendLevel(level)
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
        if (secondstowait != "") {
            WinClose(title, text, secondstowait, extitle, extext)
        } else {
            WinClose(title, text,, extitle, extext)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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
        if (secondstowait != "") {
            WinKill(title, text, secondstowait, extitle, extext)
        } else {
            WinKill(title, text,, extitle, extext)
        }
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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
        WinMaximize(title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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
        ahkid := WinGetID(title, text, extitle, extext)
        if (ahkid = "") {
            return FormatNoValueResponse()
        }
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

    if (ctrList.Length != ctrListID.Length) {
        return FormatResponse("ahk.message.ExceptionResponseMessage", "Control hwnd/class lists have unexpected lengths")
    }

    output := Format("('{}', [", ahkid)

    for index, hwnd in ctrListID {
        classname := ctrList[index]
        output .= Format("('{}', '{}'), ", hwnd, classname)

    }
    output .= "])"
    response := FormatResponse("ahk.message.WindowControlListResponseMessage", output)
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
        WinSetTitle(new_title, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }

    if (toggle = "On") {
        toggle := 1
    } else if (toggle = "Off") {
        toggle := 0
    } else if (toggle = "") {
        toggle := 1
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
        WinSetEnabled(1, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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
        WinSetEnabled(0, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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
        CoordMode("Pixel", coord_mode)
    }

    if (x2 = "A_ScreenWidth") {
        x2 := A_ScreenWidth
    }
    if (y2 = "A_ScreenHeight") {
        y2 := A_ScreenHeight
    }

    try {
        if (ImageSearch(&xpos, &ypos, x1, y1, x2, y2, imagepath) = 1) {
            s := FormatResponse("ahk.message.CoordinateResponseMessage", Format("({}, {})", xpos, ypos))
        } else {
            s := FormatNoValueResponse()
        }
    }
    finally {
        if (coord_mode != "") {
            CoordMode("Pixel", current_mode)
        }
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
        CoordMode("Pixel", coord_mode)
    }

    try {
        color := PixelGetColor(x, y, options)
    }
    finally {
        if (coord_mode != "") {
            CoordMode("Pixel", current_mode)
        }
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
        CoordMode("Pixel", coord_mode)
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
            CoordMode("Pixel", current_mode)
        }
    }

    return ret

    {% endblock AHKPixelSearch %}
}

AHKMouseGetPos(args*) {
    {% block AHKMouseGetPos %}

    coord_mode := args[1]
    current_coord_mode := Format("{}", A_CoordModeMouse)
    if (coord_mode != "") {
        CoordMode("Mouse", coord_mode)
    }
    MouseGetPos(&xpos, &ypos)

    payload := Format("({}, {})", xpos, ypos)
    resp := FormatResponse("ahk.message.CoordinateResponseMessage", payload)

    if (coord_mode != "") {
        CoordMode("Mouse", current_coord_mode)
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

    if IsInteger(state)
        return FormatResponse("ahk.message.IntegerResponseMessage", state)

    if IsFloat(state)
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
    if (coord_mode != "") {
        CoordMode("Mouse", coord_mode)
    }



    if (send_mode != "") {
        SendMode send_mode
    }

    if (relative != "") {
        MouseMove(x, y, speed, "R")
    } else {
        MouseMove(x, y, speed)
    }

    if (send_mode != "") {
        SendMode current_send_mode
    }

    if (coord_mode != "") {
        CoordMode("Mouse", current_coord_mode)
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
        SendMode send_mode
    }

    if (relative_to != "") {
        CoordMode("Mouse", relative_to)
    }

    Click(x, y, button, direction, r)

    if (relative_to != "") {
        CoordMode("Mouse", current_coord_rel)
    }

    if (send_mode != "") {
        SendMode current_send_mode
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
    CoordMode(target, relative_to)

    return FormatNoValueResponse()
    {% endblock AHKSetCoordMode %}
}


AHKGetSendMode(args*) {
    return FormatResponse("ahk.message.StringResponseMessage", A_SendMode)
}


AHKSetSendMode(args*) {
    mode := args[1]
    SendMode mode
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
    send_mode := args[9]
    current_coord_rel := Format("{}", A_CoordModeMouse)
    current_send_mode := Format("{}", A_SendMode)

    if (send_mode != "") {
        SendMode send_mode
    }

    if (relative_to != "") {
        CoordMode("Mouse", relative_to)
    }

    if (speed = "") {
        speed := A_DefaultMouseSpeed
    }

    if (x1 = "" and y1 = "") {
        MouseClickDrag(button, , , x2, y2, speed, relative)
    }
    else {
        MouseClickDrag(button, x1, y1, x2, y2, speed, relative)
    }


    if (relative_to != "") {
        CoordMode("Mouse", current_coord_rel)
    }

    if (send_mode != "") {
        SendMode current_send_mode
    }

    return FormatNoValueResponse()

    {% endblock AHKMouseClickDrag %}
}

AHKRegRead(args*) {
    {% block RegRead %}

    key_name := args[1]
    value_name := args[2]

    output := RegRead(key_name, value_name)
    resp := FormatResponse("ahk.message.StringResponseMessage", Format("{}", output))
    return resp
    {% endblock RegRead %}
}

AHKRegWrite(args*) {
    {% block RegWrite %}
    value_type := args[1]
    key_name := args[2]
    value_name := args[3]
    value := args[4]
;    RegWrite(value_type, key_name, value_name, value)
    if (value_name != "") {
        RegWrite(value, value_type, key_name, value_name)
    } else {
        RegWrite(value, value_type, key_name)
    }
    return FormatNoValueResponse()
    {% endblock RegWrite %}
}

AHKRegDelete(args*) {
    {% block RegDelete %}

    key_name := args[1]
    value_name := args[2]
    if (value_name != "") {
        RegDelete(key_name, value_name)
    } else {
        RegDelete(key_name)
    }
    return FormatNoValueResponse()

    {% endblock RegDelete %}
}

AHKKeyWait(args*) {
    {% block AHKKeyWait %}

    keyname := args[1]
    options := args[2]

    if (options = "") {
        ret := KeyWait(keyname)
    } else {
        ret := KeyWait(keyname, options)
    }

    if (ret = 0) {
        return FormatResponse("ahk.message.BooleanResponseMessage", 0)
    } else {
        return FormatResponse("ahk.message.BooleanResponseMessage", 1)
    }
    {% endblock AHKKeyWait %}
}

;SetKeyDelay(args*) {
;    {% block SetKeyDelay %}
;    SetKeyDelay(args[1], args[2])
;    {% endblock SetKeyDelay %}
;}

AHKSend(args*) {
    {% block AHKSend %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
    send_mode := args[4]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)
    current_send_mode := Format("{}", A_SendMode)

    if (send_mode != "") {
        SendMode send_mode
    }

    if (key_delay != "" or key_press_duration != "") {
        if (key_delay != "" and key_press_duration != "") {
            SetKeyDelay(key_delay, key_press_duration)
        } else if (key_delay != "" and key_press_duration = "") {
            SetKeyDelay(key_delay)
        } else if (key_delay = "" and key_press_duration != "") {
            SetKeyDelay(current_delay, key_press_duration)
        }
    }


    Send(str)

    if (send_mode != "") {
        SendMode current_send_mode
    }

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSend %}
}

AHKSendRaw(args*) {
    {% block AHKSendRaw %}
    str := args[1]
    key_delay := args[2]
    key_press_duration := args[3]
    current_delay := Format("{}", A_KeyDelay)
    current_key_duration := Format("{}", A_KeyDuration)

    if (key_delay != "" or key_press_duration != "") {
        if (key_delay != "" and key_press_duration != "") {
            SetKeyDelay(key_delay, key_press_duration)
        } else if (key_delay != "" and key_press_duration = "") {
            SetKeyDelay(key_delay)
        } else if (key_delay = "" and key_press_duration != "") {
            SetKeyDelay(current_delay, key_press_duration)
        }
    }

    Send("{Raw}" str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
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
        if (key_delay != "" and key_press_duration != "") {
            SetKeyDelay(key_delay, key_press_duration)
        } else if (key_delay != "" and key_press_duration = "") {
            SetKeyDelay(key_delay)
        } else if (key_delay = "" and key_press_duration != "") {
            SetKeyDelay(current_delay, key_press_duration)
        }
    }

    SendInput(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
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
        if (key_delay != "" and key_press_duration != "") {
            SetKeyDelay(key_delay, key_press_duration)
        } else if (key_delay != "" and key_press_duration = "") {
            SetKeyDelay(key_delay)
        } else if (key_delay = "" and key_press_duration != "") {
            SetKeyDelay(current_delay, key_press_duration)
        }
    }

    SendEvent(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
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
        if (key_delay != "" and key_press_duration != "") {
            SetKeyDelay(key_delay, key_press_duration)
        } else if (key_delay != "" and key_press_duration = "") {
            SetKeyDelay(key_delay)
        } else if (key_delay = "" and key_press_duration != "") {
            SetKeyDelay(current_delay, key_press_duration)
        }
    }

    SendPlay(str)

    if (key_delay != "" or key_press_duration != "") {
        SetKeyDelay(current_delay, current_key_duration)
    }
    return FormatNoValueResponse()
    {% endblock AHKSendPlay %}
}

AHKSetCapsLockState(args*) {
    {% block AHKSetCapsLockState %}
    state := args[1]
    if (state = "") {
        SetCapsLockState(!GetKeyState("CapsLock", "T"))
    } else {
        SetCapsLockState(state)
    }
    return FormatNoValueResponse()
    {% endblock AHKSetCapsLockState %}
}


AHKSetNumLockState(args*) {
    {% block AHKSetNumLockState %}
    state := args[1]
    if (state = "") {
        SetNumLockState(!GetKeyState("NumLock", "T"))
    } else {
        SetNumLockState(state)
    }
    return FormatNoValueResponse()
    {% endblock AHKSetNumLockState %}
}


AHKSetScrollLockState(args*) {
    {% block AHKSetScrollLockState %}
    state := args[1]
    if (state = "") {
        SetScrollLockState(!GetKeyState("ScrollLock", "T"))
    } else {
        SetScrollLockState(state)
    }
    return FormatNoValueResponse()
    {% endblock AHKSetScrollLockState %}
}

HideTrayTip(args*) {
    {% block HideTrayTip %}
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        A_IconHidden := true
        Sleep 200 ; It may be necessary to adjust this sleep.
        A_IconHidden := false
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

AHKControlClick(args*) {
    {% block AHKControlClick %}

    ctrl := IsNumber(args[1]) ? Number(args[1]) : args[1]
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
        ControlClick(ctrl || unset, title, text, button, click_count, options, exclude_title, exclude_text)
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

AHKControlGetText(args*) {
    {% block AHKControlGetText %}

    ctrl := IsNumber(args[1]) ? Number(args[1]) : args[1]
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

AHKControlGetPos(args*) {
    {% block AHKControlGetPos %}

    ctrl := IsNumber(args[1]) ? Number(args[1]) : args[1]
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

AHKControlSend(args*) {
    {% block AHKControlSend %}
    ctrl := IsNumber(args[1]) ? Number(args[1]) : args[1]
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
        ControlSend(keys, ctrl || unset, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
    return FormatNoValueResponse()
    {% endblock AHKControlSend %}
}

AHKWinFromMouse(args*) {
    {% block AHKWinFromMouse %}

    MouseGetPos(,, &MouseWin)

    if (MouseWin = "") {
        return FormatNoValueResponse()
    }

    return FormatResponse("ahk.message.WindowResponseMessage", MouseWin)
    {% endblock AHKWinFromMouse %}
}

AHKWinIsAlwaysOnTop(args*) {
    {% block AHKWinIsAlwaysOnTop %}
    ; TODO: detect hidden windows / etc?
    title := args[1]
    ExStyle := WinGetExStyle(title)
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
        SetTitleMatchMode(match_mode)
    }
    if (match_speed != "") {
        SetTitleMatchMode(match_speed)
    }
    current_detect_hw := Format("{}", A_DetectHiddenWindows)

    if (detect_hw != "") {
        DetectHiddenWindows(detect_hw)
    }
    if (width = "" or height = "") {
        WinGetPos(&_, &__, &w, &h, title, text, extitle, extext)
        if (width = "") {
            width := w
        }
        if (height = "") {
            height := h
        }
    }

    try {
        WinMove(x, y, width, height, title, text, extitle, extext)
    }
    finally {
        DetectHiddenWindows(current_detect_hw)
        SetTitleMatchMode(current_match_mode)
        SetTitleMatchMode(current_match_speed)
    }
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

AHKGetVolume(args*) {
    {% block AHKGetVolume %}

    device_number := args[1]

    retval := SoundGetVolume(,device_number)
    response := FormatResponse("ahk.message.FloatResponseMessage", Format("{}", retval))
    return response
    {% endblock AHKGetVolume %}
}

AHKSoundBeep(args*) {
    {% block AHKSoundBeep %}
    freq := args[1]
    duration := args[2]
    SoundBeep(freq, duration)
    return FormatNoValueResponse()
    {% endblock AHKSoundBeep %}
}

AHKSoundGet(args*) {
    {% block AHKSoundGet %}
    return FormatResponse("ahk.message.ExceptionResponseMessage", "SoundGet is not supported in ahk v2")
    {% endblock AHKSoundGet %}
}

AHKSoundSet(args*) {
    {% block AHKSoundSet %}
    return FormatResponse("ahk.message.ExceptionResponseMessage", "SoundSet is not supported in ahk v2")
    {% endblock AHKSoundSet %}
}

AHKSoundPlay(args*) {
    {% block AHKSoundPlay %}
    filename := args[1]
    SoundPlay(filename)
    return FormatNoValueResponse()
    {% endblock AHKSoundPlay %}
}

AHKSetVolume(args*) {
    {% block AHKSetVolume %}
    device_number := args[1]
    value := args[2]
    SoundSetVolume(value,,device_number)
    return FormatNoValueResponse()
    {% endblock AHKSetVolume %}
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

    TrayTip(text, title, option)
    return FormatNoValueResponse()
    {% endblock AHKTraytip %}
}

AHKShowToolTip(args*) {
    {% block AHKShowToolTip %}
    text := args[1]
    x := args[2]
    y := args[3]
    which := args[4]

    ToolTip(text, IsNumber(x) ? Number(x) : unset, IsNumber(y) ? Number(y) : unset, which || unset)
    ; In AHK v2, doubling the call to ToolTip seems necessary to ensure synchronous creation of the window
    ; This seems to be more reliable than sleeping to wait for the tooltip callback
    ; Without this doubled up call (or a sleep) we return the the blocking loop (awaiting next command from Python)
    ;  before the tooltip window is created, meaning the tooltip will not show until if/when processing the next command
    ToolTip(text, IsNumber(x) ? Number(x) : unset, IsNumber(y) ? Number(y) : unset, which || unset)
    return FormatNoValueResponse()
    {% endblock AHKShowToolTip %}
}

AHKGetClipboard(args*) {
    {% block AHKGetClipboard %}

    return FormatResponse("ahk.message.StringResponseMessage", A_Clipboard)
    {% endblock AHKGetClipboard %}
}

AHKGetClipboardAll(args*) {
    {% block AHKGetClipboardAll %}
    data := ClipboardAll()
    return FormatBinaryResponse(&data)
    {% endblock AHKGetClipboardAll %}
}

AHKSetClipboard(args*) {
    {% block AHKSetClipboard %}
    text := args[1]
    A_Clipboard := text
    return FormatNoValueResponse()
    {% endblock AHKSetClipboard %}
}

AHKSetClipboardAll(args*) {
    {% block AHKSetClipboardAll %}
    ; TODO there should be a way for us to accept a base64 string instead
    filename := args[1]
    contents := FileRead(filename, "RAW")
    A_Clipboard := ClipboardAll(contents)
    return FormatNoValueResponse()
    {% endblock AHKSetClipboardAll %}
}

AHKClipWait(args*) {

    timeout := args[1]
    wait_for_any_data := args[2]

    if ClipWait(timeout, wait_for_any_data)
        return FormatNoValueResponse()
    else
        return FormatResponse("ahk.message.TimeoutResponseMessage", "timed out waiting for clipboard data")
    return FormatNoValueResponse()
}

AHKBlockInput(args*) {
    value := args[1]
    BlockInput(value)
    return FormatNoValueResponse()
}

AHKMenuTrayTip(args*) {
    value := args[1]
    A_IconTip := value
    return FormatNoValueResponse()
}

AHKMenuTrayShow(args*) {
    A_IconHidden := 0
    return FormatNoValueResponse()
}

AHKMenuTrayHide(args*) {
    A_IconHidden := 1
    return FormatNoValueResponse()
}

AHKMenuTrayIcon(args*) {
    filename := args[1]
    icon_number := args[2]
    freeze := args[3]
    TraySetIcon(filename, icon_number, freeze)
    return FormatNoValueResponse()
}

;AHKGuiNew(args*) {
;
;    options := args[1]
;    title := args[2]
;    Gui(New, options, title)
;    return FormatResponse("ahk.message.StringResponseMessage", hwnd)
;}

AHKMsgBox(args*) {

    options := args[1]
    title := args[2]
    text := args[3]
    timeout := args[4]
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

AHKFileSelectFile(args*) {

    options := args[1]
    root := args[2]
    title := args[3]
    filter := args[4]
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

AHKFileSelectFolder(args*) {

    starting_folder := args[1]
    options := args[2]
    prompt := args[3]

    output := DirSelect(starting_folder, options, prompt)

    if (output = "") {
        ret := FormatNoValueResponse()
    } else {
        ret := FormatResponse("ahk.message.StringResponseMessage", output)
    }
    return ret
}

Crypt32 := DllCall("LoadLibrary", "Str", "Crypt32.dll", "Ptr")

b64decode(&pszString) {
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
;    buff_size := 0 ; The function will write to this variable on our first call
    pdwSkip := 0 ; We don't use any headers or preamble, so this is zero
    pdwFlags := 0 ; We don't need this, so make it null

    ; The first call calculates the required size. The result is written to pbBinary
    success := DllCall("Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(pszString), "UInt", cchString, "UInt", dwFlags, "UInt", getsize, "UIntP", &buff_size := 0, "Int", pdwSkip, "Int", pdwFlags )
    if (success = 0) {
        return ""
    }

    ; We're going to give a pointer to a variable to the next call, but first we want to make the buffer the correct size using VarSetCapacity using the previous return value
    ret := Buffer(buff_size)

    ; Now that we know the buffer size we need and have the variable's capacity set to the proper size, we'll pass a pointer to the variable for the decoded value to be written to

    success := DllCall( "Crypt32.dll\CryptStringToBinary", "Ptr", StrPtr(pszString), "UInt", cchString, "UInt", dwFlags, "Ptr", ret.Ptr, "UIntP", &buff_size, "Int", pdwSkip, "Int", pdwFlags )
    if (success=0) {
        return ""
    }
    return StrGet(ret, "UTF-8")
}


b64encode(&data) {
    ; REF: https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptbinarytostringa
    ;  [in]            const BYTE *pbBinary: A pointer to the array of bytes to be converted into a string.
    ;  [in]            DWORD      cbBinary: The number of elements in the pbBinary array.
    ;  [in]            DWORD      dwFlags: Specifies the format of the resulting formatted string (see table in REF)
    ;  [out, optional] LPSTR      pszString: A pointer to the string, or null (0) to calculate size
    ;  [in, out]       DWORD      *pcchString: A pointer to a DWORD variable that contains the size, in TCHARs, of the pszString buffer

    cbBinary := data.Size
    if (cbBinary = 0) {
        return ""
    }
    dwFlags := 0x00000001 | 0x40000000  ; CRYPT_STRING_BASE64 + CRYPT_STRING_NOCRLF

    ; First step is to get the size so we can set the capacity of our return buffer correctly
    success := DllCall("Crypt32.dll\CryptBinaryToString", "Ptr", data, "UInt", cbBinary, "UInt", dwFlags, "Ptr", 0, "UIntP", &buff_size := 0)
    if (success = 0) {
        msg := Format("Problem converting data to base64 when calling CryptBinaryToString ({})", A_LastError)
        throw Error(msg, -1)
    }

    VarSetStrCapacity(&ret, buff_size * 2)

    ; Now we do the conversion to base64 and rteturn the string

    success := DllCall("Crypt32.dll\CryptBinaryToString", "Ptr", data, "UInt", cbBinary, "UInt", dwFlags, "Str", ret, "UIntP", &buff_size)
    if (success = 0) {
        msg := Format("Problem converting data to base64 when calling CryptBinaryToString ({})", A_LastError)
        throw Error(msg, -1)
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
        decoded_value := b64decode(&encoded_value)
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
    if (query = "") {
        ; Technically, this should only happen if the Python process has died, so sending a message is probably futile
        ; But if this somehow triggers in some other case and the Python process is still listening, we'll try to have an informative error raised.
        pyresp := FormatResponse("ahk.message.ExceptionResponseMessage", "Unexpected empty message; AHK exiting. This is likely a bug. Please report this issue at https://github.com/spyoungtech/ahk/issues")
        stdout.Write(pyresp)
        stdout.Read(0)
        ; Exit to avoid leaving the process hanging around
        ExitApp
    }
    argsArray := CommandArrayFromQuery(query)
    try {
        func_name := argsArray[1]
        argsArray.RemoveAt(1)
        {% block before_function %}
        {% endblock before_function %}
        pyresp := %func_name%(argsArray*)
        {% block after_function %}
        {% endblock after_function %}
    } catch Any as e {
        {% block function_error_handle %}
        message := Format("Error occurred in {} (line {}). The error message was: {}. Specifically: {}`nStack:`n{}", e.what, e.line, e.message, e.extra, e.stack)
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
