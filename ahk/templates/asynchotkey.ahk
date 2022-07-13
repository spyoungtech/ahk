{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    FileAppend, `n, *, UTF-8
    return
{% endblock body %}
