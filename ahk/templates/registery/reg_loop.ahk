{% extends "base.ahk" %}
{% block body %}
Loop, {{ reg }}, {{ key_name }}, {{ mode }}
{% endblock body %}
