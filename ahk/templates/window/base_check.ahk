{% extends "base.ahk" %}
{% block body %}
if {{ command }}("ahk_id {{ win.id }}") {
    FileAppend, 1, *
else
	FileAppend, 0, *
{% endblock body %}
