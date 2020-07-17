{% extends "base.ahk"%}
{% block body %}
TrayTip {{ title }}, {{ text }}, {{ second }}, {{ option }}
Sleep {{ second * 1000 }}
HideTrayTip()

; Copy this function into your script to use it.
HideTrayTip() {
    TrayTip ; Attempt to hide it the normal way.
    if SubStr(A_OSVersion,1,3) = "10." {
        Menu Tray, NoIcon
        Sleep 200 ; It may be necessary to adjust this sleep.
        Menu Tray, Icon
    }
}
{% endblock body %}
