from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingAddress, OrderNote

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

class OrderNoteInline(admin.TabularInline):
    model = OrderNote
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'first_name', 'last_name', 'total_price', 'status', 'paid',
        'payment_method', 'transaction_id', 'payment_proof_display', 'created_at'
    ]
    list_filter = ['status', 'paid', 'created_at', 'payment_method']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'transaction_id']
    inlines = [OrderItemInline, OrderNoteInline]
    readonly_fields = [
        'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at',
        'payment_proof_display', 'payment_details_display'
    ]
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Information', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Order Details', {
            'fields': ('status', 'shipping_cost', 'total_price')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'transaction_id', 'payment_proof_display', 'payment_details_display', 'paid')
        }),
        ('Credit Card Information', {
            'fields': ('card_number', 'card_expiry', 'card_name'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at')
        }),
    )
    
    def payment_details_display(self, obj):
        """Display payment details in a formatted way"""
        if obj.payment_method == 'CARD' and (obj.card_number or obj.card_expiry or obj.card_name):
            return format_html(
                '<strong>Card Payment Details:</strong><br>'
                'Card Number: {}<br>'
                'Expiry Date: {}<br>'
                'Name on Card: {}',
                obj.card_number or 'Not provided',
                obj.card_expiry or 'Not provided',
                obj.card_name or 'Not provided'
            )
        elif obj.payment_method in ['MTN_MOBILE_MONEY', 'AIRTEL_MONEY']:
            return format_html(
                '<strong>Mobile Money Details:</strong><br>'
                'Transaction ID: {}<br>'
                'Payment Proof: {}',
                obj.transaction_id or 'Not provided',
                'Provided' if obj.payment_proof else 'Not provided'
            )
        elif obj.payment_method == 'CASH':
            return 'Cash payment'
        else:
            return 'No payment details available'
    payment_details_display.short_description = "Payment Details Summary"

    def payment_proof_display(self, obj):
        if obj.payment_proof:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height:60px; max-width:120px; border:1px solid #ccc; border-radius:6px; box-shadow:0 2px 8px #eee;" class="admin-payment-proof-img" /></a>',
                obj.payment_proof.url, obj.payment_proof.url
            )
        return "No proof uploaded"
    payment_proof_display.short_description = "Payment Proof"
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            if obj.status == Order.SHIPPED and not obj.shipped_at:
                obj.shipped_at = timezone.now()
            elif obj.status == Order.DELIVERED and not obj.delivered_at:
                obj.delivered_at = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'city', 'country', 'is_default']
    list_filter = ['is_default', 'country', 'city']
    search_fields = ['first_name', 'last_name', 'address', 'city', 'country']


@admin.register(OrderNote)
class OrderNoteAdmin(admin.ModelAdmin):
    list_display = ['order', 'note_type', 'content', 'created_at']
    list_filter = ['note_type', 'created_at']
    search_fields = ['content', 'order__id']
    readonly_fields = ['created_at']
