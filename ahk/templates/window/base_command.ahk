{% extends "base.ahk" %}
{% block body %}
{{ command }}, {{ title }}{% if seconds_to_wait %}, {{ seconds_to_wait }}{% endif %}
{% endblock body %}
