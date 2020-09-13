{% extends "base.ahk" %}
{% block body %}
if (GetKeyState("{{ key_name }}"{% if mode %} , "{{ mode }}"{% endif %})) {
    FileAppend, 1, *
} else {
    FileAppend, 0, *
}
{% endblock body %}