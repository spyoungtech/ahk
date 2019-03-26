{% extends "base.ahk" %}
{% block body %}
SoundBeep, {{ frequency }}, {{ duration }}
{% endblock body %}
