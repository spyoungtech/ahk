{% extends "base.ahk" %}
{% block body %}
WinRestore, ahk_id {{ win.id }}
{% endblock body %}
