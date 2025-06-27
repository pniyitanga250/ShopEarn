from django.core.management.base import BaseCommand
from dashboard_finances.models import ExchangeRate
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialize exchange rates for all supported currencies'

    def handle(self, *args, **options):
        # Default exchange rates (as of June 2023)
        # These would typically be fetched from an API in a production environment
        default_rates = {
            'USD': Decimal('1.0'),  # Base currency
            'RWF': Decimal('1200.0'),  # Rwandan Franc
            'BIF': Decimal('2800.0'),  # Burundian Franc
            'KES': Decimal('130.0'),   # Kenyan Shilling
            'UGX': Decimal('3700.0'),  # Ugandan Shilling
            'CDF': Decimal('2500.0'),  # Congolese Franc
            'TZS': Decimal('2400.0'),  # Tanzanian Shilling
        }
        
        created_count = 0
        updated_count = 0
        
        for currency_code, rate in default_rates.items():
            exchange_rate, created = ExchangeRate.objects.update_or_create(
                currency_code=currency_code,
                defaults={
                    'exchange_rate': rate,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created exchange rate for {currency_code}: {rate}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated exchange rate for {currency_code}: {rate}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully initialized exchange rates: {created_count} created, {updated_count} updated'
        ))