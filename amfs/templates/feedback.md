# {{ report['name'] }} - Feedback

**Submission ID:** {{ submission['id'] }}\
**Overall mark:** {{ submission['mark'] }}/{{ report['full_mark'] }}

{% if submission['failed_tests']|length > 0 %}
**Failed tests:**
{% for link in submission['failed_tests'] %}
- {{ link }}
{% endfor %}
{% endif %}

{% if submission['passed_tests']|length > 0 %}
**Passed tests:**
{% for link in submission['passed_tests'] %}
- {{ link }}
{% endfor %}
{% endif %}

{% if submission['feedback']|length > 0 %}
## Instructor Feedback

{% for feedback in submission['feedback'] %}
- {{ feedback }}
{% endfor %}

{% endif %}
## Test Case Breakdown

{% for attempt in submission['attempts'] %}
### {{ attempt['name'] }}

_**{{ attempt['code'] }}**_
```
{{ attempt['output'] }}
```
{% endfor %}
