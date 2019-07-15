{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    {{ script }}
    FileAppend, Hotkey Fired, *
    ExitApp
{% endblock body %}