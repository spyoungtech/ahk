{% extends "base.ahk"%}
{% block body %}
ToolTip, {{ text }}, {{ x }}, {{ y }}, {{ id }}
Sleep, {{ second }}
ToolTip ,,,, {{ id }}
{% endblock body %}
