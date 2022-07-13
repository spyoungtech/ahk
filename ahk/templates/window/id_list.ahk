{% extends "base.ahk" %}
{% block body %}
WinGet windows, List
Loop %windows%
{
    id := windows%A_Index%
    r .= id . "`,"
}
FileAppend, %r%, *, UTF-8
{% endblock body %}
