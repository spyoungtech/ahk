{% extends "base.ahk" %}
{% block body %}
WinMinimize, ahk_id {{ win.id }}
{% endblock body %}
