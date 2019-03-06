{% extends "base.ahk" %}
{% block body %}
KeyWait, {{ key_name }}{% if options %} , {{ options }}{% endif %}
{% endblock body %}