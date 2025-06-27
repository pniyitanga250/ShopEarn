from django.test import TestCase
from decimal import Decimal
from .models import ExchangeRate


class ExchangeRateModelTests(TestCase):
    def setUp(self):
        # Create test exchange rates
        ExchangeRate.objects.create(
            currency_code='USD',
            exchange_rate=Decimal('1.0'),
            is_active=True
        )
        ExchangeRate.objects.create(
            currency_code='RWF',
            exchange_rate=Decimal('1200.0'),
            is_active=True
        )
        ExchangeRate.objects.create(
            currency_code='KES',
            exchange_rate=Decimal('130.0'),
            is_active=True
        )
        ExchangeRate.objects.create(
            currency_code='UGX',
            exchange_rate=Decimal('3700.0'),
            is_active=False  # Inactive rate
        )
    
    def test_get_rate(self):
        """Test retrieving exchange rates"""
        self.assertEqual(ExchangeRate.get_rate('USD'), Decimal('1.0'))
        self.assertEqual(ExchangeRate.get_rate('RWF'), Decimal('1200.0'))
        self.assertEqual(ExchangeRate.get_rate('KES'), Decimal('130.0'))
        
        # Test non-existent currency
        self.assertEqual(ExchangeRate.get_rate('EUR'), Decimal('1.0'))
        
        # Test inactive currency
        self.assertEqual(ExchangeRate.get_rate('UGX'), Decimal('1.0'))
    
    def test_get_currency_for_country(self):
        """Test getting currency code for country code"""
        self.assertEqual(ExchangeRate.get_currency_for_country('RW'), 'RWF')
        self.assertEqual(ExchangeRate.get_currency_for_country('KE'), 'KES')
        self.assertEqual(ExchangeRate.get_currency_for_country('US'), 'USD')  # Default
    
    def test_get_currency_symbol(self):
        """Test getting currency symbol"""
        self.assertEqual(ExchangeRate.get_currency_symbol('USD'), '$')
        self.assertEqual(ExchangeRate.get_currency_symbol('RWF'), 'FRw')
        self.assertEqual(ExchangeRate.get_currency_symbol('KES'), 'KSh')
    
    def test_convert_price(self):
        """Test price conversion"""
        # Test USD to RWF conversion
        converted_price, symbol, code = ExchangeRate.convert_price(
            Decimal('100'), country_code='RW'
        )
        self.assertEqual(converted_price, Decimal('120000'))
        self.assertEqual(symbol, 'FRw')
        self.assertEqual(code, 'RWF')
        
        # Test USD to KES conversion
        converted_price, symbol, code = ExchangeRate.convert_price(
            Decimal('50'), country_code='KE'
        )
        self.assertEqual(converted_price, Decimal('6500'))
        self.assertEqual(symbol, 'KSh')
        self.assertEqual(code, 'KES')
        
        # Test with direct currency code
        converted_price, symbol, code = ExchangeRate.convert_price(
            Decimal('25'), currency_code='RWF'
        )
        self.assertEqual(converted_price, Decimal('30000'))
        self.assertEqual(symbol, 'FRw')
        self.assertEqual(code, 'RWF')
        
        # Test with non-existent country code (should default to USD)
        converted_price, symbol, code = ExchangeRate.convert_price(
            Decimal('10'), country_code='US'  # US is not in our country mapping
        )
        self.assertEqual(converted_price, Decimal('10'))
        self.assertEqual(symbol, '$')
        self.assertEqual(code, 'USD')
