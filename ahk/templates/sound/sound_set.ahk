{% extends "base.ahk" %}
{% block body %}
SoundSet, {{ value }}, {{ component_type }}, {{ control_type }}, {{ device_number }}
FileAppend, %retval%, *
{% endblock body %}
