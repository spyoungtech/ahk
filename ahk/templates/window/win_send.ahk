{% extends "base.ahk" %}
{% block body %}
SetKeyDelay, {{ delay }}, {{ press_duration }}

{% if raw %}ControlSendRaw{% else %}ControlSend{% endif %}, , {{ keys }}, {{ title }}
{% endblock body %}
