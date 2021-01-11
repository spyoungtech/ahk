{% extends "base.ahk" %}
{% block body %}
{% if delay %}SetKeyDelay, {{ delay }}{% endif %}

Send{% if raw %}Raw{% endif %},{{ s }}
{% endblock body %}