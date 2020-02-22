{% extends "base.ahk" %}
{% block body %}
{% if raw %}ControlSendRaw{% else %}ControlSend{% endif %}, , {{ keys }}, {{ title }}
{% endblock body %}
