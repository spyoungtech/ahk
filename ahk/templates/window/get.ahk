{% extends "base.ahk" %}
{% block body %}
WinGet, output,{{ subcommand }},{{ title }},{{ text }},{{ exclude_title }},{{ exclude_text }}
FileAppend, %output%, *
{% endblock body %}
