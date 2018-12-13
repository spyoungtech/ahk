{% block directives %}
{% for directive in directives %}
{{ directive }}
{% endfor %}
{% endblock %}

{% block body %}
{% endblock body %}

{% block exit %}
ExitApp
{% endblock exit %}
