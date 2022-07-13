{% extends "base.ahk" %}
{% block body %}
if (GetKeyState("{{ key_name }}"{% if mode %} , "{{ mode }}"{% endif %})) {
    FileAppend, 1, *, UTF-8
} else {
    FileAppend, 0, *, UTF-8
}
{% endblock body %}
