{% extends "base.ahk" %}
{% block body %}
{% if delay %}SetKeyDelay, {{ delay }}{% endif %}

ControlSend{% if raw %}Raw{% endif %},, {{ s }}, AHK_ID {{ hwnd }}
{% endblock body %}
