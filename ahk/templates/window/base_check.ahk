{% extends "base.ahk" %}
{% block body %}
if {{ command }}("{{ title }}")
    FileAppend, 1, *
else
    FileAppend, 0, *
{% endblock body %}
