{% extends "base.ahk" %}
{% block body %}
WinMove,{{ title }},,{{ x }},{{ y }}{% if width or height %},{% if width %}{{ width }}{% endif %},{% if height %}{{ height }}{% endif %}{% endif %}
{% endblock body %}
