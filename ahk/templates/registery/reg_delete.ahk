{% extends "base.ahk" %}
{% block body %}
RegDelete,{{ key_name }},{{ value_name }}
{% endblock body %}
