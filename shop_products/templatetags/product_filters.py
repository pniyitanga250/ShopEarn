from django import template
from decimal import Decimal
from dashboard_finances.models import ExchangeRate

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return value - arg
    except (ValueError, TypeError):
        try:
            return Decimal(value) - Decimal(arg)
        except:
            return 0

@register.filter
def div(value, arg):
    """Divide the value by the arg."""
    try:
        return value / arg
    except (ValueError, TypeError, ZeroDivisionError):
        try:
            return Decimal(value) / Decimal(arg) if Decimal(arg) != 0 else 0
        except:
            return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the arg."""
    try:
        return value * arg
    except (ValueError, TypeError):
        try:
            return Decimal(value) * Decimal(arg)
        except:
            return 0
            
@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the key.
    Usage: {{ mydict|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def get_currency_symbol_for_country(country_code):
    """
    Get currency symbol for a country code
    Usage: {{ user.country|get_currency_symbol_for_country }}
    """
    currency_code = ExchangeRate.get_currency_for_country(country_code)
    return ExchangeRate.get_currency_symbol(currency_code)

@register.filter
def convert_currency(price_usd, country_code):
    """
    Convert price from USD to local currency based on user's country
    Usage: {{ product.price|convert_currency:user.country }}
    
    Returns the converted price as a decimal
    """
    if not price_usd or not country_code:
        return price_usd
        
    try:
        converted_price, _, _ = ExchangeRate.convert_price(price_usd, country_code=country_code)
        return converted_price
    except Exception:
        return price_usd

@register.simple_tag
def display_price(price_usd, country_code=None):
    """
    Display price in local currency with proper formatting
    Usage: {% display_price product.price user.country %}
    
    Returns formatted string with currency symbol
    """
    if not price_usd:
        return "$0.00"
        
    if not country_code:
        return f"${price_usd}"
        
    try:
        converted_price, currency_symbol, _ = ExchangeRate.convert_price(price_usd, country_code=country_code)
        
        # Format based on currency - some use whole numbers, others use decimals
        if currency_symbol in ['FRw', 'FBu', 'USh', 'FC', 'TSh']:
            # These currencies typically don't use decimal places in everyday transactions
            formatted_price = f"{int(converted_price):,}"
        else:
            # Use 2 decimal places for other currencies
            formatted_price = f"{float(converted_price):,.2f}"
            
        return f"{currency_symbol} {formatted_price}"
    except Exception as e:
        # Fallback to USD
        return f"${price_usd}"