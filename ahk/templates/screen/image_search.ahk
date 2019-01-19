{% extends "base.ahk" %}
{% block body %}
CoordMode Pixel, {{ coord_mode }}
ImageSearch, xpos, ypos, {{ x1 }}, {{ y1 }}, {{ x2 }}, {{ y2 }}, {% if scale_width %}*w{{ scale_width}} *h{{ scale_height }} {% endif %}{{ image_path }}
s .= Format("({}, {})", xpos, ypos)
FileAppend, %s%, *
{% endblock body %}
