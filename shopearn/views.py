from django.shortcuts import render
from shop_products.models import Product


def home(request):
    """
    Home page view
    """
    # Get featured products (for example, the 3 most recent products)
    featured_products = Product.objects.filter(available=True).order_by('-created_at')[:3]
    
    context = {
        'featured_products': featured_products,
    }
    
    return render(request, 'home.html', context)