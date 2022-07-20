{% extends "base.ahk" %}
{% block body %}
{% if exact %}
WinWait,{{title}},{{text}},{{timeout}},{{exclude_title}},{{exclude_text}}
{% else %}
SetTitleMatchMode 2
WinWait,{{title}},{{text}},{{timeout}},{{exclude_title}},{{exclude_text}}
SetTitleMatchMode 1
{% endif %}
if !ErrorLevel
{
       WinGet, output, ID
       FileAppend,%output%,*, UTF-8
}
{% endblock body %}
