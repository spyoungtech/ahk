{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    {{ script }}
    FileAppend, Hotkey, %A_WorkingDir%tmp/{{ file_name }}
    return
{% endblock body %}