from django.urls import path
from . import views

app_name = 'dashboard_finances'

urlpatterns = [
    path('', views.finances, name='dashboard_finances'),
    path('exchange-rates/', views.exchange_rates_list, name='exchange_rates_list'),
    path('exchange-rates/update/<int:id>/', views.update_exchange_rate, name='update_exchange_rate'),
    path('api/convert-price/', views.get_converted_price, name='get_converted_price'),
]
