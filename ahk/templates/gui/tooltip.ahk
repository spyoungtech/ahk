{% extends "base.ahk"%}
{% block body %}
ToolTip, {{ text }}, {{ x }}, {{ y }}, {{ id }}
Sleep, {{ second * 1000 }}
ToolTip ,,,, {{ id }}
{% endblock body %}
