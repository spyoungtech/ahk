{% extends "base.ahk" %}
{% block body %}
RegRead,output,{{ key_name }},{{ value_name }}
FileAppend, %output%, *
{% endblock body %}
