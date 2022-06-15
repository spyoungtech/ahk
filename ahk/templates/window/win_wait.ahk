{% extends "base.ahk" %}
{% block body %}
WinWait,{{title}},{{text}},{{timeout}},{{exclude_title}},{{exclude_text}}
if !ErrorLevel
{
       WinGet, output, ID
       FileAppend,%output%,*
}
{% endblock body %}
