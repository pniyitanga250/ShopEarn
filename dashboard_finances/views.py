from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import ExchangeRate
from decimal import Decimal


def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_staff


def finances(request):
    return render(request, 'dashboard_finances/finances.html')


@login_required
@user_passes_test(is_admin)
def exchange_rates_list(request):
    """
    Display and manage exchange rates
    """
    exchange_rates = ExchangeRate.objects.all().order_by('currency_code')
    
    context = {
        'exchange_rates': exchange_rates,
        'active_tab': 'exchange_rates',
    }
    
    return render(request, 'dashboard_finances/exchange_rates.html', context)


@login_required
@user_passes_test(is_admin)
def update_exchange_rate(request, id):
    """
    Update an exchange rate
    """
    exchange_rate = get_object_or_404(ExchangeRate, id=id)
    
    if request.method == 'POST':
        try:
            new_rate = Decimal(request.POST.get('exchange_rate', '0'))
            is_active = request.POST.get('is_active') == 'on'
            
            if new_rate <= 0:
                messages.error(request, 'Exchange rate must be greater than zero')
                return redirect('dashboard_finances:exchange_rates_list')
            
            exchange_rate.exchange_rate = new_rate
            exchange_rate.is_active = is_active
            exchange_rate.save()
            
            messages.success(request, f'Exchange rate for {exchange_rate.get_currency_code_display()} updated successfully')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid exchange rate value')
    
    return redirect('dashboard_finances:exchange_rates_list')


@login_required
def get_converted_price(request):
    """
    API endpoint to get converted price based on user's country
    """
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        price_usd = Decimal(request.GET.get('price', '0'))
        country_code = request.user.country if request.user.is_authenticated else None
        
        if not country_code:
            return JsonResponse({
                'converted_price': str(price_usd),
                'currency_symbol': '$',
                'currency_code': 'USD'
            })
        
        converted_price, currency_symbol, currency_code = ExchangeRate.convert_price(
            price_usd, country_code=country_code
        )
        
        return JsonResponse({
            'converted_price': str(converted_price),
            'currency_symbol': currency_symbol,
            'currency_code': currency_code
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
