{% extends "base.ahk" %}
{% block body %}
ControlSend, , {{ keys }}, ahk_id {{ win.id }}
{% endblock body %}