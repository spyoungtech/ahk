{% extends "base.ahk" %}
{% block body %}
WinGet, ExStyle, ExStyle, {{win._title}}, {{win._text}}, {{win._exclude_title}}, {{win._exclude_text}}
if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
    FileAppend, 1, *
else
    FileAppend, 0, *
{% endblock body %}