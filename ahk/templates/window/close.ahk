{% extends "base.ahk" %}
{% block body %}
WinClose, {{win.title}}, {{win.text}}, {{seconds_to_wait}}, {{win._exclude_title}}, {{win._exclude_text}}
{% endblock body %}