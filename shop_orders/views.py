from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem, ShippingAddress, OrderNote
from shop_products.models import Product
from decimal import Decimal


class Cart:
    """
    Shopping cart class
    """
    def __init__(self, request):
        """
        Initialize the cart
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Save an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.get_display_price()),
                'name': product.name
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """
        Mark the session as modified to make sure it gets saved
        """
        self.session.modified = True
    
    def remove(self, product):
        """
        Remove a product from the cart
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database
        """
        product_ids = self.cart.keys()
        # Get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Count all items in the cart
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """
        Calculate the total price of all items in the cart
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        """
        Remove cart from session
        """
        del self.session['cart']
        self.save()
    
    def get_total_product_value(self):
        """
        Calculate the total product value of all items in the cart
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total_value = Decimal('0.00')
        for product in products:
            item = self.cart[str(product.id)]
            value = getattr(product, 'product_value', Decimal('0.00'))
            total_value += Decimal(value) * item['quantity']
        return total_value


def cart_add(request, product_id):
    """
    Add a product to the cart
    """
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    override_quantity = request.POST.get('override', False) == 'True'
    
    cart.add(product=product, quantity=quantity, override_quantity=override_quantity)
    messages.success(request, f'{product.name} added to your cart.')
    
    return redirect('shop_orders:cart')


def cart_remove(request, product_id):
    """
    Remove a product from the cart
    """
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from your cart.')
    
    return redirect('shop_orders:cart')


def cart_clear(request):
    """
    Clear all items from the cart
    """
    if request.method == 'POST':
        cart = Cart(request)
        cart.clear()
        messages.success(request, 'Your cart has been cleared.')
    
    return redirect('shop_orders:cart')


def cart_detail(request):
    """
    Display the cart details
    """
    cart = Cart(request)
    
    # Get shipping addresses for logged in users
    shipping_addresses = []
    if request.user.is_authenticated:
        shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'cart': cart,
        'shipping_addresses': shipping_addresses
    }
    
    return render(request, 'orders/cart.html', context)


@login_required
def checkout(request):
    """
    Checkout view
    """
    cart = Cart(request)
    
    # Check if cart is empty
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop_orders:cart')
    
    # Get user's shipping addresses
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        'cart': cart,
        'shipping_addresses': shipping_addresses
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def order_create(request):
    """
    Create a new order
    """
    if request.method != 'POST':
        return redirect('shop_orders:checkout')
    
    cart = Cart(request)
    
    # Check if cart is empty
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop_orders:cart')
        
    # Log all form data for debugging (in a real app, you'd use proper logging)
    print("Form data received:", request.POST)
    print("Files received:", request.FILES)
    
    # Create a note with all form data for admin reference
    form_data_note = "Form data submitted by customer:\n"
    for key, value in request.POST.items():
        if key != 'csrfmiddlewaretoken':  # Skip CSRF token
            form_data_note += f"{key}: {value}\n"
    
    # Add file information
    if request.FILES:
        form_data_note += "\nFiles submitted:\n"
        for key, value in request.FILES.items():
            form_data_note += f"{key}: {value.name} ({value.size} bytes)\n"
    
    # Get form data
    address_id = request.POST.get('address_id')
    payment_method = request.POST.get('payment_method')
    transaction_id = request.POST.get('transaction_id', '')
    payment_proof = request.FILES.get('payment_proof')
    
    # Get credit card information if payment method is CARD
    card_number = ''
    card_expiry = ''
    card_name = ''
    if payment_method == 'CARD':
        card_number_full = request.POST.get('card_number', '')
        # Store only last 4 digits for security
        card_number = f"xxxx-xxxx-xxxx-{card_number_full[-4:]}" if card_number_full and len(card_number_full) >= 4 else ''
        card_expiry = request.POST.get('expiry', '')
        card_name = request.POST.get('card_name', '')
    
    # If using an existing address
    if address_id:
        shipping_address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
        first_name = shipping_address.first_name
        last_name = shipping_address.last_name
        address = shipping_address.address
        city = shipping_address.city
        state = shipping_address.state
        postal_code = shipping_address.postal_code
        country = shipping_address.country
        phone = shipping_address.phone
    else:
        # Using a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        
        # Save as new address if requested
        if request.POST.get('save_address'):
            ShippingAddress.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                phone=phone,
                is_default=request.POST.get('is_default', False)
            )
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        first_name=first_name,
        last_name=last_name,
        email=request.user.email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        total_price=cart.get_total_price(),
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_proof=payment_proof,
        card_number=card_number,
        card_expiry=card_expiry,
        card_name=card_name,
    )
    
    # Create order items
    for item in cart:
        product = item['product']
        OrderItem.objects.create(
            order=order,
            product=product,
            price=item['price'],
            quantity=item['quantity'],
            product_value=getattr(product, 'product_value', product.price)
        )
    
    # Save form data as a note for admin reference
    OrderNote.objects.create(
        order=order,
        note_type='SYSTEM',
        content=form_data_note
    )
    
    # Clear the cart
    cart.clear()
    
    # Process payment (in a real application)
    # For now, just mark the order as paid
    # Only mark as paid if not Mobile Money (for demo, you may adjust logic as needed)
    if payment_method not in ['MTN_MOBILE_MONEY', 'AIRTEL_MONEY']:
        order.mark_as_paid(transaction_id=transaction_id, payment_method=payment_method)
    
    messages.success(request, 'Your order has been placed successfully.')
    return redirect('shop_orders:order_detail', order_id=order.id)


@login_required
def order_history(request):
    """
    Display user's order history
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """
    Display order details
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def upload_payment_proof(request, order_id):
    """
    Upload payment proof for an order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow uploading payment proof for pending orders with mobile money payment
    if order.status != Order.PENDING or order.payment_method not in ['MTN_MOBILE_MONEY', 'AIRTEL_MONEY']:
        messages.error(request, "Payment proof can only be uploaded for pending mobile money orders.")
        return redirect('shop_orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id', '')
        payment_proof = request.FILES.get('payment_proof')
        
        if not payment_proof:
            messages.error(request, "Please select a payment proof image to upload.")
            return redirect('shop_orders:order_detail', order_id=order.id)
        
        # Update order with payment proof and transaction ID
        order.transaction_id = transaction_id
        order.payment_proof = payment_proof
        order.save()
        
        # Create a note about the payment proof
        OrderNote.objects.create(
            order=order,
            note_type='SYSTEM',
            content=f"Payment proof uploaded by customer. Transaction ID: {transaction_id}"
        )
        
        messages.success(request, "Your payment proof has been uploaded successfully.")
        return redirect('shop_orders:order_detail', order_id=order.id)
    
    # If not POST, redirect to order detail
    return redirect('shop_orders:order_detail', order_id=order.id)


@login_required
def cancel_order(request, order_id):
    """
    Cancel an order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow cancellation of pending or processing orders
    if order.status not in [Order.PENDING, Order.PROCESSING]:
        messages.error(request, "This order cannot be cancelled.")
        return redirect('shop_orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        cancel_reason = request.POST.get('cancel_reason')
        other_reason = request.POST.get('other_reason')
        
        # Combine reasons if "Other" was selected
        if cancel_reason == 'Other' and other_reason:
            cancel_reason = f"Other: {other_reason}"
        
        # Update order status
        order.status = Order.CANCELLED
        order.save()
        
        # Create a note about the cancellation
        OrderNote.objects.create(
            order=order,
            note_type='CANCELLATION',
            content=f"Order cancelled by customer. Reason: {cancel_reason}"
        )
        
        messages.success(request, "Your order has been cancelled successfully.")
        return redirect('shop_orders:order_history')
    
    # If not POST, redirect to order detail
    return redirect('shop_orders:order_detail', order_id=order.id)
