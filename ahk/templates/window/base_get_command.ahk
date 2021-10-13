{% extends "base.ahk" %}
{% block body %}
{{ command }},text,{{ title }}
FileAppend, %text%, *
{% endblock body %}
