{% extends "base.ahk" %}
{% block body %}
RegWrite,{{ value_type }},{{ key_name }},{{ value_name }}
{% endblock body %}
