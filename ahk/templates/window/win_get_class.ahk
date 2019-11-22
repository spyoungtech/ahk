{% extends "base.ahk" %}
{% block body %}
WinGetClass, text, ahk_id {{ win.id }}
FileAppend, %text%, *
{% endblock body %}
