from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """
    Product categories
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('shop_products:product_list_by_category', args=[self.slug])


class Product(models.Model):
    """
    Product model
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Discounts and promotions
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_on_sale = models.BooleanField(default=False)
    
    # Inventory management
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    
    # Product value field (for internal calculations)
    product_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product value for internal calculations")
    
    # Relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Media
    main_image = models.ImageField(upload_to='products/')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Ensure product_value is set; default to price if not set
        if self.product_value is None or self.product_value == '':
            self.product_value = self.price
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('shop_products:product_detail', args=[self.id, self.slug])
    
    def get_display_price(self):
        """Return the current display price (regular or discount)"""
        if self.is_on_sale and self.discount_price:
            return self.discount_price
        return self.price
    
    @property
    def is_in_stock(self):
        return self.stock > 0 and self.available


class ProductImage(models.Model):
    """
    Additional product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductReview(models.Model):
    """
    Product reviews by customers (authenticated or anonymous)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('shop_accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    anonymous_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name for anonymous reviewer")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s review of {self.product.name}"
        elif self.anonymous_name:
            return f"Anonymous ({self.anonymous_name}) review of {self.product.name}"
        else:
            return f"Anonymous review of {self.product.name}"
