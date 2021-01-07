{% extends "base.ahk" %}
{% block body %}
WinGetPos, x, y, width, height, {{ title }}
{% if pos_info %}
{% if pos_info == "position" %}
s .= Format("({}, {})", x, y)
{% elif pos_info == "height" %}
s .= Format("({})", height)
{% elif pos_info == "width" %}
s .= Format("({})", width)
{% endif %}
{% else %}
s .= Format("({}, {}, {}, {})", x, y, width, height)
{% endif %}
FileAppend, %s%, *
{% endblock body %}
