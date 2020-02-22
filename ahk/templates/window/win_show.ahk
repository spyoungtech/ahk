{% extends "base.ahk" %}
{% block body %}
WinShow, ahk_id {{ win.id }}
{% endblock body %}
