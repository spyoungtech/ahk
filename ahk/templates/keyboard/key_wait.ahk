{% extends "base.ahk" %}
{% block body %}
KeyWait, {{ key_name }}{% if options %} , {{ options }}{% endif %}

FileAppend, %ErrorLevel%, *
{% endblock body %}