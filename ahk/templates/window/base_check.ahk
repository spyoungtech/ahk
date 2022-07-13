{% extends "base.ahk" %}
{% block body %}
if {{ command }}("{{ title }}")
    FileAppend, 1, *, UTF-8
else
    FileAppend, 0, *, UTF-8
{% endblock body %}
