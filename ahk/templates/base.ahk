{% block directives %}
#NoEnv
#NoTrayIcon
{% for directive in directives %}
{{ directive }}
{% endfor %}
{% endblock %}

{% block body %}
{{ body }}
{% endblock body %}

{% block exit %}
ExitApp
{% endblock exit %}
