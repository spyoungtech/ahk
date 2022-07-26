{% extends "base.ahk" %}
{% block body %}
{% if match_mode %}
SetTitleMatchMode, {{ match_mode }}
{% endif %}
{% if match_speed %}
SetTitleMatchMode, {{ match_speed }}
{% endif %}
WinWait,{{title}},{{text}},{{timeout}},{{exclude_title}},{{exclude_text}}
if !ErrorLevel
{
       WinGet, output, ID
       FileAppend,%output%,*, UTF-8
}
{% endblock body %}
