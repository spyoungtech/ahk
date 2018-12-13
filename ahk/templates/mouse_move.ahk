{% extends "base.ahk" %}
{% block body %}
CoordMode Mouse, {{mode}}
MouseMove, {{x}}, {{y}}, {{speed}}{% if relative %}, R{% endif %}
{% endblock body %}