{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    {{ script }}
    FileAppend, Hotkey Fired, *
{% endblock body %}