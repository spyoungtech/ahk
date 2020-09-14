{% extends "base.ahk" %}
{% block body %}
SetCapsLockState, {{state}}
{% endblock body %}