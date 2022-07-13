{% extends "base.ahk" %}
{% block body %}
{{ command }},text,{{ title }}
FileAppend, %text%, *, UTF-8
{% endblock body %}
