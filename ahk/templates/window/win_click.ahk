{% extends "base.ahk" %}
{% block body %}
ControlClick, x{{ x }} y{{ y }}, {{ hwnd }},, {{ button }}, {{ n }}{% if options %}, {{ options }}{% endif %}
{% endblock body %}
