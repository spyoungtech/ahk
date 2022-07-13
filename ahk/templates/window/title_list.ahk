{% extends "base.ahk" %}
{% block body %}
WinGet windows, List
Loop %windows%
{
    id := windows%A_Index%
    WinGetTitle wt, ahk_id %id%
    r .= wt . "`n"
}
FileAppend, %r%, *, UTF-8
{% endblock body %}
