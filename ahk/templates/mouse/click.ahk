{% extends "base.ahk" %}
{% block body %}
CoordMode Mouse, {{mode}}
Click{% if args %}, {{ args }}{% endif %}
{% endblock %}
