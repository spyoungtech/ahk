{% extends "base.ahk" %}
{% block body %}
{{ hotkey }}::
    FileAppend, `n, *
    return
{% endblock body %}
