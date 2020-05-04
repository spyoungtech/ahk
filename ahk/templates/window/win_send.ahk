{% extends "base.ahk" %}
{% block body %}
{% if delay %}SetKeyDelay, {{ delay }}{% endif %}

{% if raw %}ControlSendRaw{% else %}ControlSend{% endif %}, , {{ keys }}, {{ title }}
{% endblock body %}
