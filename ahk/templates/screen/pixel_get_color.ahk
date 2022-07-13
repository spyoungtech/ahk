{% extends "base.ahk" %}
{% block body %}
CoordMode, Pixel, {{ coord_mode }}
PixelGetColor,color, {{ x }}, {{ y }}{% if options %},{% for option in options %} {{ option }}{% endfor %}{% endif %}

FileAppend, %color%, *, UTF-8
{% endblock body %}
