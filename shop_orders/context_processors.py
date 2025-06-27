from .views import Cart

def cart_processor(request):
    """
    Context processor to add cart information to all templates
    """
    cart = Cart(request)
    return {
        'cart_count': len(cart)
    }