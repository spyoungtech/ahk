{% extends "base.ahk" %}
{% block body %}
Run, {{ target }}, {{working_dir}}, {{options}}, output
{% if wait %}
WinWait, ahk_pid %output%
WinGet, output, ID, ahk_pid %output%
{% endif %}
FileAppend, %output%, *
{% endblock body %}
