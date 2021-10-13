{% extends "base.ahk" %}
{% block body %}
CoordMode,Mouse,{{mode}}
MouseGetPos, xpos, ypos
s .= Format("({}, {})", xpos, ypos)
FileAppend, %s%, *
{% endblock body %}