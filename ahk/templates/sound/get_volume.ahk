{% extends "base.ahk" %}
{% block body %}
SoundGetWaveVolume, retval, {{ device_number }}
FileAppend, %retval%, *, UTF-8
{% endblock body %}
