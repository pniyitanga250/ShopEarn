from django.db import models
from django.conf import settings
from django.utils import timezone
from shop_products.models import Product


class Order(models.Model):
    """
    Order model for tracking customer purchases
    """
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'
    REFUNDED = 'REFUNDED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
        (REFUNDED, 'Refunded'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment information
    PAYMENT_METHOD_CHOICES = [
        ('', 'Select Payment Method'),
        ('MTN_MOBILE_MONEY', 'MTN Mobile Money'),
        ('AIRTEL_MONEY', 'Airtel Money'),
        ('CARD', 'Card'),
        ('CASH', 'Cash'),
    ]
    payment_method = models.CharField(max_length=50, blank=True, null=True, choices=PAYMENT_METHOD_CHOICES, default='')
    transaction_id = models.CharField(max_length=100, blank=True, help_text="Transaction ID (TxId) for Mobile Money payments")
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True, help_text="Upload payment proof (screenshot)")
    
    # Credit card information (stored securely in a real application)
    card_number = models.CharField(max_length=19, blank=True, help_text="Credit card number (last 4 digits only)")
    card_expiry = models.CharField(max_length=5, blank=True, help_text="Credit card expiry date (MM/YY)")
    card_name = models.CharField(max_length=100, blank=True, help_text="Name on credit card")
    
    paid = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    def get_total_cost(self):
        """Calculate total cost of all items in the order"""
        return sum(item.get_cost() for item in self.items.all()) + self.shipping_cost
    
    def mark_as_paid(self, transaction_id=None, payment_method=None):
        """Mark the order as paid"""
        self.paid = True
        self.status = self.PROCESSING
        self.paid_at = timezone.now()
        
        if transaction_id:
            self.transaction_id = transaction_id
        if payment_method:
            self.payment_method = payment_method
            
        self.save(update_fields=['paid', 'status', 'paid_at', 'transaction_id', 'payment_method'])
        return True
    
    def get_total_product_value(self):
        """Calculate the total product value of this order"""
        return sum(item.get_product_value() for item in self.items.all())


class OrderItem(models.Model):
    """
    Individual items within an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    # Track product value at the time of order
    product_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product value at time of order", default=0)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.id}"

    def get_cost(self):
        """Calculate cost of this item"""
        return self.price * self.quantity

    def get_product_value(self):
        """Calculate product value (PV) of this item"""
        return self.product_value * self.quantity


class ShippingAddress(models.Model):
    """
    Saved shipping addresses for users
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'
        ordering = ['-is_default', '-updated_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        # If this address is being set as default, unset any other default
        if self.is_default:
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class OrderNote(models.Model):
    """
    Notes and comments on orders
    """
    SYSTEM = 'SYSTEM'
    ADMIN = 'ADMIN'
    CUSTOMER = 'CUSTOMER'
    CANCELLATION = 'CANCELLATION'
    REFUND = 'REFUND'
    
    NOTE_TYPES = [
        (SYSTEM, 'System'),
        (ADMIN, 'Admin'),
        (CUSTOMER, 'Customer'),
        (CANCELLATION, 'Cancellation'),
        (REFUND, 'Refund'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notes')
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default=SYSTEM)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_note_type_display()} note on Order {self.order.id}"
