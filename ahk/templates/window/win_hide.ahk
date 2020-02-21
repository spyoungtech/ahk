{% extends "base.ahk" %}
{% block body %}
WinHide, ahk_id {{ win.id }}
{% endblock body %}
