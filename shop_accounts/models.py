from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model for ShopEarn platform
    """
    # Country choices with currency initials
    COUNTRY_CHOICES = [
        ('RW', 'Rwanda (RWF)'),
        ('BI', 'Burundi (BIF)'),
        ('KE', 'Kenya (KES)'),
        ('UG', 'Uganda (UGX)'),
        ('CD', 'DR Congo (CDF)'),
        ('TZ', 'Tanzania (TZS)'),
    ]
    
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    join_date = models.DateField(default=timezone.now)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    def get_country_display_name(self):
        """
        Returns the country name with currency initial
        """
        if self.country:
            country_dict = {
                'RW': 'Rwanda (RWF)',
                'BI': 'Burundi (BIF)',
                'KE': 'Kenya (KES)',
                'UG': 'Uganda (UGX)',
                'CD': 'DR Congo (CDF)',
                'TZ': 'Tanzania (TZS)',
            }
            return country_dict.get(self.country, '')
        return 'Not provided'


class ContactMessage(models.Model):
    """
    Model to store contact form submissions
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.subject} - {self.name}"
