{% extends "base.ahk" %}
{% block body %}
WinGetPos, x, y, width, height, {{win.title}}, {{win.text}}, {{win._exclude_title}}, {{win._exclude_text}}
s .= Format("({}, {}, {}, {})", x, y, width, height)
FileAppend, %s%, *
{% endblock body %}
