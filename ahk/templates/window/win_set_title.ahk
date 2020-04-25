{% extends "base.ahk" %}
{% block body %}
WinSetTitle, {{ title }}, {{ text }}, {{ new_title }}
{% endblock body %}
