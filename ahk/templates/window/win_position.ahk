{% extends "base.ahk" %}
{% block body %}
WinGetPos, x, y, width, height, {{ title }}
s .= Format("({}, {}, {}, {})", x, y, width, height)
FileAppend, %s%, *
{% endblock body %}
