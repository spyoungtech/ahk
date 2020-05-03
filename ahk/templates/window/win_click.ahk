{% extends "base.ahk" %}
{% block body %}
ControlClick, x{{ x }} y{{ y }}, {{ hwnd }}
{% endblock body %}
