{% if pos_info %}
AHKWinGetPos,{{ title }},{{ pos_info }}
{% else %}
AHKWinGetPos,{{ title }}
{% endif %}