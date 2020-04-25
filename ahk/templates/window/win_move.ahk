{% extends "base.ahk" %}
{% block body %}
WinMove, {{ title }}, , {{ x }}, {{ y }}{% if width %}, {{ width }}{% endif %}{% if height %}, {{ height }}{% endif %}
{% endblock body %}
