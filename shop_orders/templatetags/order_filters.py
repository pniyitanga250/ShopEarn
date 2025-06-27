from django import template

register = template.Library()

@register.filter
def split_string(value, delimiter=','):
    """
    Split a string by a delimiter and return a list
    Usage: {{ "value1,value2"|split_string:"," }}
    """
    return value.split(delimiter)

@register.filter
def in_list(value, list_string):
    """
    Check if a value is in a comma-separated list
    Usage: {{ value|in_list:"value1,value2,value3" }}
    """
    return value in list_string.split(',')