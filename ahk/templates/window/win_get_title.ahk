{% extends "base.ahk" %}
{% block body %}
WinGetTitle, title, ahk_id {{ win.id }}
FileAppend, %title%, *
{% endblock body %}
