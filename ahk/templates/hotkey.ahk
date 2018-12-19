{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    {{ script }}
    return
{% endblock body %}
