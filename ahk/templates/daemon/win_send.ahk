SetKeyDelay,{{ delay }},{{ press_duration }}
{% if raw %}WinSendRaw{% else %}WinSend{% endif %},{{ title }},{{ keys }}