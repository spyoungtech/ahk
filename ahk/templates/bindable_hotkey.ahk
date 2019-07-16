{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    {{ script }}
    FileAppend, Hotkey, hotkey_file
    return
{% endblock body %}