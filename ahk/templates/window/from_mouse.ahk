{% extends "base.ahk" %}
{% block body %}
MouseGetPos,,, MouseWin
FileAppend, %MouseWin%, *, UTF-8
{% endblock body %}
