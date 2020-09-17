{% extends "base.ahk" %}
{% block body %}
{% if state %}SetCapsLockState, {{state}}{% else %}SetCapsLockState % !GetKeyState("CapsLock", "T"){% endif %}
{% endblock body %}