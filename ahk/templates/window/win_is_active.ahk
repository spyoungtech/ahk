{% extends "base.ahk" %}
{% block body %}
if WinActive("ahk_id {{ win.id }}") {
    FileAppend, 1, *
    ExitApp
}
FileAppend, 0, *
ExitApp
{% endblock body %}
