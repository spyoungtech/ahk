{% extends "base.ahk" %}
{% block body %}
ControlSend,{{ control }},{{ keys }},{{ win_title }},{{ win_text }},{{ exclude_title }},{{ exclude_text }}
{% endblock body %}