{% extends "base.ahk" %}
{% block body %}
{{ command }}, ahk_id {{ win.id }}{% if seconds_to_wait %}, {{ seconds_to_wait }}{% endif %}, {{ title }}, {{ text }}, {{ exclude_title }}, {{ exclude_text }}
{% endblock body %}
