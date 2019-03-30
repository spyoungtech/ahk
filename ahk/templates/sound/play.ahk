{% extends "base.ahk" %}
{% block body %}
SoundPlay, {{ filename }}{% if wait %}, {{ wait }}{% endif %}
{% endblock body %}
