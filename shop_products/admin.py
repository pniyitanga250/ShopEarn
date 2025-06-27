from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductReview

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'image_display', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_display']
    
    def image_display(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    image_display.short_description = 'Image'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'is_on_sale', 'stock', 'available', 'main_image_display', 'created_at']
    list_filter = ['category', 'is_on_sale', 'available', 'created_at']
    list_editable = ['price', 'discount_price', 'is_on_sale', 'stock', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductReviewInline]
    readonly_fields = ['main_image_display']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'is_on_sale')
        }),
        ('Inventory', {
            'fields': ('stock', 'available')
        }),
        ('Additional Information', {
            'fields': ('product_value',)
        }),
        ('Media', {
            'fields': ('main_image', 'main_image_display')
        }),
    )
    
    def main_image_display(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.main_image.url)
        return "No Image"
    main_image_display.short_description = 'Preview'

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'anonymous_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'anonymous_name', 'comment']
