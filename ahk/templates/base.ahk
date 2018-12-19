{% block directives %}
#NoEnv
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
