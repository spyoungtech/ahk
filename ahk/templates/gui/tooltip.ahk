{% extends "base.ahk"%}
{% block body %}
ToolTip, {{ text }}, {{ x }}, {{ y }}, {{ id }}
Sleep, {{ ms }}
ToolTip ,,,, {{ id }}
{% endblock body %}
