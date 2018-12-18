{% extends "base.ahk" %}
{% block body %}
WinClose, ahk_id {{ win.id }}, {{seconds_to_wait}}
{% endblock body %}