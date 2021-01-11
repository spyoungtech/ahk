{% extends "base.ahk" %}
{% block body %}
{% if delay %}SetKeyDelay, {{ delay }}{% endif %}

SendPlay,{{ s }}
{% endblock body %}