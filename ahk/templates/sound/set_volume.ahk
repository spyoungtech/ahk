{% extends "base.ahk" %}
{% block body %}
SoundSetWaveVolume, {{ value }}, {{ device_number }}
{% endblock body %}
