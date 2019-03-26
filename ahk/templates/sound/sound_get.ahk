{% extends "base.ahk" %}
{% block body %}
SoundGet, retval , {{ component_type }}, {{ control_type }}, {{ device_number }}
FileAppend, %retval%, *
{% endblock body %}
