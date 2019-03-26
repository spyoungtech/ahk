{% extends "base.ahk" %}
{% block body %}
SoundGetWaveVolume, retval, {{ device_number }}
FileAppend, %retval%, *
{% endblock body %}
