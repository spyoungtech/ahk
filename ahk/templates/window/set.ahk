{% extends "base.ahk" %}
{% block body %}
WinSet, {{subcommand}}, {{value}}, {{win.title}}, {{win.text}}, {{win._exclude_title}}, win._exclude_text}}
{% endblock body %}