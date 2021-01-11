{% extends "base.ahk" %}
{% block body %}
{% if delay %}SetKeyDelay, {{ delay }}{% endif %}

SendEvent,{{ s }}
{% endblock body %}