from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.cache import cache
from decimal import Decimal

class ExchangeRate(models.Model):
    """
    Model to store exchange rates for different countries
    Base currency is USD
    """
    CURRENCY_CHOICES = [
        ('RWF', 'Rwandan Franc'),
        ('BIF', 'Burundian Franc'),
        ('KES', 'Kenyan Shilling'),
        ('UGX', 'Ugandan Shilling'),
        ('CDF', 'Congolese Franc'),
        ('TZS', 'Tanzanian Shilling'),
        ('USD', 'US Dollar'),
    ]
    
    # Map country codes to currency codes
    COUNTRY_TO_CURRENCY = {
        'RW': 'RWF',
        'BI': 'BIF',
        'KE': 'KES',
        'UG': 'UGX',
        'CD': 'CDF',
        'TZ': 'TZS',
    }
    
    # Currency symbols
    CURRENCY_SYMBOLS = {
        'RWF': 'FRw',
        'BIF': 'FBu',
        'KES': 'KSh',
        'UGX': 'USh',
        'CDF': 'FC',
        'TZS': 'TSh',
        'USD': '$',
    }
    
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICES, unique=True)
    exchange_rate = models.DecimalField(
        max_digits=12, 
        decimal_places=4,
        help_text="Exchange rate from USD (1 USD = X local currency)"
    )
    last_updated = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_currency_code_display()} (1 USD = {self.exchange_rate} {self.currency_code})"
    
    def clean(self):
        if self.currency_code == 'USD' and self.exchange_rate != 1:
            raise ValidationError("Exchange rate for USD must be 1.0")
    
    def save(self, *args, **kwargs):
        # Clear cache when exchange rates are updated
        cache_keys = [f'exchange_rate_{self.currency_code}', 'all_exchange_rates']
        for key in cache_keys:
            cache.delete(key)
        
        # Ensure USD always has exchange rate of 1
        if self.currency_code == 'USD':
            self.exchange_rate = 1
            
        self.last_updated = timezone.now()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_rate(cls, currency_code):
        """Get exchange rate for a specific currency"""
        cache_key = f'exchange_rate_{currency_code}'
        rate = cache.get(cache_key)
        
        if rate is None:
            try:
                exchange_rate = cls.objects.get(currency_code=currency_code, is_active=True)
                rate = exchange_rate.exchange_rate
                # Cache for 24 hours
                cache.set(cache_key, rate, 60*60*24)
            except cls.DoesNotExist:
                # Default to 1.0 if no exchange rate is found
                rate = Decimal('1.0')
        
        return rate
    
    @classmethod
    def get_currency_for_country(cls, country_code):
        """Get currency code for a country code"""
        return cls.COUNTRY_TO_CURRENCY.get(country_code, 'USD')
    
    @classmethod
    def get_currency_symbol(cls, currency_code):
        """Get currency symbol for a currency code"""
        return cls.CURRENCY_SYMBOLS.get(currency_code, '$')
    
    @classmethod
    def convert_price(cls, price_usd, country_code=None, currency_code=None):
        """
        Convert price from USD to local currency
        
        Args:
            price_usd: Price in USD
            country_code: Country code (e.g., 'RW')
            currency_code: Currency code (e.g., 'RWF')
            
        Returns:
            tuple: (converted_price, currency_symbol, currency_code)
        """
        if not currency_code and country_code:
            currency_code = cls.get_currency_for_country(country_code)
        
        if not currency_code:
            currency_code = 'USD'
            
        rate = cls.get_rate(currency_code)
        converted_price = Decimal(price_usd) * rate
        currency_symbol = cls.get_currency_symbol(currency_code)
        
        return (converted_price, currency_symbol, currency_code)
