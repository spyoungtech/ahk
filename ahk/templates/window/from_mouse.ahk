{% extends "base.ahk" %}
{% block body %}
MouseGetPos,,, MouseWin
FileAppend, %MouseWin%, *
{% endblock body %}
