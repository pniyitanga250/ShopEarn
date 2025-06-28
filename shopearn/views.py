from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
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


def sitemap_view(request):
    """
    Generate a sitemap.xml file
    """
    # Get all available products for the sitemap
    products = Product.objects.filter(available=True)
    
    context = {
        'products': products,
    }
    
    sitemap_content = render_to_string('sitemap.xml', context)
    return HttpResponse(sitemap_content, content_type='application/xml')


def robots_txt(request):
    """
    Serve robots.txt file
    """
    robots_content = render_to_string('robots.txt')
    return HttpResponse(robots_content, content_type='text/plain')


def google_verification(request):
    """
    Google Search Console verification page
    """
    return render(request, 'google-site-verification.html')