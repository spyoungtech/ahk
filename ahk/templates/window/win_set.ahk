{% extends "base.ahk" %}
{% block body %}
WinSet,{{subcommand}},{{value}},{{ title }}
{% endblock body %}
