{% extends "base.ahk" %}
{% block body %}
WinGetText, text, ahk_id {{ win.id }}
FileAppend, %text%, *
{% endblock body %}
