from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, ProductReview
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from shop_orders.models import Order, OrderItem


def product_list(request, category_slug=None):
    """
    Display a list of products, optionally filtered by category
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(description__icontains=search_query)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Handle sorting
    sort = request.GET.get('sort', 'default')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'sort': sort,
        'search_query': search_query
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, id, slug):
    """
    Display product details
    """
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    reviews = product.reviews.all()

    # Calculate average rating
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0

    # Get related products
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    # Handle review submission (allow anonymous)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')
        anonymous_name = request.POST.get('anonymous_name', '').strip()
        user = request.user if request.user.is_authenticated else None

        if rating > 0:
            if user:
                # Check if user already reviewed this product
                existing_review = ProductReview.objects.filter(product=product, user=user).first()
                if existing_review:
                    existing_review.rating = rating
                    existing_review.comment = comment
                    existing_review.save()
                    messages.success(request, 'Your review has been updated.')
                else:
                    ProductReview.objects.create(
                        product=product,
                        user=user,
                        rating=rating,
                        comment=comment
                    )
                    messages.success(request, 'Your review has been submitted.')
            else:
                # Anonymous review
                ProductReview.objects.create(
                    product=product,
                    user=None,
                    anonymous_name=anonymous_name or 'Anonymous',
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'Your anonymous review has been submitted.')

            # Recalculate average rating
            reviews = product.reviews.all()
            avg_rating = sum(review.rating for review in reviews) / len(reviews)

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
    }

    return render(request, 'products/product_detail.html', context)


def product_search_api(request):
    """
    API endpoint for live product search
    """
    from dashboard_finances.models import ExchangeRate
    
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(available=True)
    products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    
    # Limit to 12 products for performance
    products = products[:12]
    
    # Get user's country for currency conversion
    user_country = None
    if request.user.is_authenticated and request.user.country:
        user_country = request.user.country
    
    result = []
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
            'price': str(product.price),
            'url': reverse('shop_products:product_detail', args=[product.id, product.slug]),
            'is_on_sale': product.is_on_sale,
            'is_in_stock': product.is_in_stock,
        }
        
        if product.is_on_sale and product.discount_price:
            product_data['discount_price'] = str(product.discount_price)
        
        if product.main_image:
            product_data['image_url'] = product.main_image.url
        
        # Add currency information if user is logged in and has a country set
        if user_country:
            # Get converted price and currency symbol
            converted_price, currency_symbol, currency_code = ExchangeRate.convert_price(
                product.price, country_code=user_country
            )
            
            product_data['converted_price'] = str(converted_price)
            product_data['currency_symbol'] = currency_symbol
            product_data['currency_code'] = currency_code
            
            if product.is_on_sale and product.discount_price:
                converted_discount, _, _ = ExchangeRate.convert_price(
                    product.discount_price, country_code=user_country
                )
                product_data['converted_discount_price'] = str(converted_discount)
        
        result.append(product_data)
    
    return JsonResponse({'products': result})


@login_required
def order_review(request, order_id):
    """
    Allow users to review products from a specific order
    """
    # Get the order and verify it belongs to the current user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if the order is delivered (only allow reviews for delivered orders)
    if order.status != Order.DELIVERED:
        messages.warning(request, 'You can only review products from delivered orders.')
        return redirect('shop_orders:order_detail', order_id=order.id)
    
    # Get all products from this order
    order_items = order.items.all()
    products = [item.product for item in order_items]
    
    # Check if user has already reviewed any of these products
    existing_reviews = {}
    for product in products:
        review = ProductReview.objects.filter(product=product, user=request.user).first()
        if review:
            existing_reviews[product.id] = review
    
    if request.method == 'POST':
        # Process the submitted reviews
        products_reviewed = []
        
        # Debug information
        print("Form data received:", request.POST)
        
        for item in order_items:
            product = item.product
            product_id_str = str(product.id)
            
            # Check if this product was reviewed in this submission
            if f'rating_{product_id_str}' in request.POST:
                rating = int(request.POST.get(f'rating_{product_id_str}', 0))
                comment = request.POST.get(f'comment_{product_id_str}', '')
                
                if rating > 0:
                    # Check if user already reviewed this product
                    existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
                    
                    if existing_review:
                        # Update existing review
                        existing_review.rating = rating
                        existing_review.comment = comment
                        existing_review.save()
                    else:
                        # Create new review
                        ProductReview.objects.create(
                            product=product,
                            user=request.user,
                            rating=rating,
                            comment=comment
                        )
                    
                    products_reviewed.append(product.name)
        
        if products_reviewed:
            messages.success(request, f'Thank you for reviewing {", ".join(products_reviewed)}!')
        
        return redirect('shop_orders:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'order_items': order_items,
        'existing_reviews': existing_reviews,
    }
    
    return render(request, 'products/order_review.html', context)
