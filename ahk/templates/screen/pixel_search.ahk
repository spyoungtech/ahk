{% extends "base.ahk" %}
{% block body %}
CoordMode Pixel, {{ coord_mode }}
PixelSearch, xpos, ypos, {{ x1 }}, {{ y1 }}, {{ x2 }}, {{ y2 }}, {{ color }} , {{ variation }}{% if options %},{% for option in options %} {{ option }}{% endfor %}{% endif %}

s .= Format("({}, {})", xpos, ypos)
FileAppend, %s%, *
{% endblock body %}
