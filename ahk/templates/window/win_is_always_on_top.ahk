{% extends "base.ahk" %}
{% block body %}
WinGet, ExStyle, ExStyle, {{ title }}
if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
    FileAppend, 1, *, UTF-8
else
    FileAppend, 0, *, UTF-8
{% endblock body %}
