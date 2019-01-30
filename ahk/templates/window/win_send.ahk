{% extends "base.ahk" %}
{% block body %}
{% if raw %}ControlSendRaw{% else %}ControlSend{% endif %}, , {{ keys }}, ahk_id {{ win.id }}
{% endblock body %}