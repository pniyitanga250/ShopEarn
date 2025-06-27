from django.urls import path
from . import views

app_name = 'shop_products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.product_search_api, name='product_search_api'),
    path('review/order/<int:order_id>/', views.order_review, name='order_review'),
]