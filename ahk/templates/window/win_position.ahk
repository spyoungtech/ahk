{% extends "base.ahk" %}
{% block body %}
WinGetPos, x, y, width, height, ahk_id {{ win.id }}
s .= Format("({}, {}, {}, {})", x, y, width, height)
FileAppend, %s%, *
{% endblock body %}
