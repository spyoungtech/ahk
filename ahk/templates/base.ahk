{% block directives %}
{% if not _daemon %}#NoEnv{% endif %}
{% for directive in directives %}
{{ directive }}
{% endfor %}
{% endblock %}

{% block body %}
{{ body }}
{% endblock body %}

{% block exit %}
{% if not _daemon %}ExitApp{% endif %}
{% endblock exit %}
