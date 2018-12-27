{% extends "base.ahk" %}
{% block body %}
CoordMode Mouse, {{mode}}
MouseClickDrag, {{button}}, {{x1}}, {{y1}}, {{x2}}, {{y2}}{% if speed %}, {{speed}}{% endif %}{% if relative %}, R{% endif %}
{% endblock body %}
