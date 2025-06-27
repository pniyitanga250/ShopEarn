from django.urls import path
from . import views

app_name = 'shop_orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('upload-payment-proof/<int:order_id>/', views.upload_payment_proof, name='upload_payment_proof'),
]