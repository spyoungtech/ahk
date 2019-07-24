{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    {{ script }}
    FileAppend, A, {{ file_path }}
    return
{% endblock body %}