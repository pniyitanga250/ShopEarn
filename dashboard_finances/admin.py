from django.contrib import admin
from .models import ExchangeRate

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency_code', 'exchange_rate', 'last_updated', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('currency_code',)
    readonly_fields = ('last_updated',)
    
    def get_readonly_fields(self, request, obj=None):
        # Make currency_code readonly if this is an existing object
        if obj:
            return self.readonly_fields + ('currency_code',)
        return self.readonly_fields
