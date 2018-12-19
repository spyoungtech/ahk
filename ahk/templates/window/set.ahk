{% extends "base.ahk" %}
{% block body %}
WinSet, {{subcommand}}{% for arg in args %}, {{ arg }}{% endfor %}
{% endblock body %}
