{% extends "base.ahk" %}
{% block body %}

ControlSend,, {{ s }}, AHK_ID {{ hwnd }}
{% endblock body %}
