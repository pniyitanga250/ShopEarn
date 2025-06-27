import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopearn.settings')
django.setup()

from django.template import Template, Context

# Test the in_list filter
template_str = """
{% load order_filters %}
Testing in_list filter:
'MTN_MOBILE_MONEY' in 'MTN_MOBILE_MONEY,AIRTEL_MONEY': {% if 'MTN_MOBILE_MONEY'|in_list:'MTN_MOBILE_MONEY,AIRTEL_MONEY' %}True{% else %}False{% endif %}
'CARD' in 'MTN_MOBILE_MONEY,AIRTEL_MONEY': {% if 'CARD'|in_list:'MTN_MOBILE_MONEY,AIRTEL_MONEY' %}True{% else %}False{% endif %}
"""

template = Template(template_str)
context = Context({})
result = template.render(context)
print(result)

# Test the split_string filter
template_str = """
{% load order_filters %}
Testing split_string filter:
'MTN_MOBILE_MONEY,AIRTEL_MONEY' split by ',': {{ 'MTN_MOBILE_MONEY,AIRTEL_MONEY'|split_string:',' }}
"""

template = Template(template_str)
context = Context({})
result = template.render(context)
print(result)