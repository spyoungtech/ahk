{% extends "base.ahk" %}
{% block body %}
{% if delay %}SetKeyDelay, {{ delay }}{% endif %}

ControlSend,, {{ s }}, AHK_ID {{ hwnd }}
{% endblock body %}
