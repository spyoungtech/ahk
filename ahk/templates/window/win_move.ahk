{% extends "base.ahk" %}
{% block body %}
WinMove, ahk_id {{ win.id }}, , {{ x }}, {{ y }}{% if width %}, {{ width }}{% endif %}{% if height %}, {{ height }}{% endif %}
{% endblock body %}