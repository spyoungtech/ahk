{% extends "base.ahk" %}
{% block body %}
CoordMode Mouse, {{mode}}
Click{% for arg in args %}, {{ arg }}{% endfor %}
{% endblock %}
