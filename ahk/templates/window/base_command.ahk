{% extends "base.ahk" %}
{% block body %}
{{ command }}, ahk_id {{ win.id }}{% if seconds_to_wait %}, {{ seconds_to_wait }}{% endif %}{% if win._exclude_title %}, {{ win._exclude_title }}{% endif %}{% if win._exclude_text %}, {{ win._exclude_text }}{% endif %}
{% endblock body %}
