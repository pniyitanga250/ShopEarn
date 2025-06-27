from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContactMessage


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_country', 'is_staff')
    
    def get_country(self, obj):
        return obj.get_country_display_name()
    get_country.short_description = 'Country'
    list_filter = ('is_staff', 'is_active', 'country')
    fieldsets = UserAdmin.fieldsets + (
        ('Account Information', {'fields': ('join_date', 'phone_number', 'date_of_birth', 'country', 'profile_picture')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


admin.site.register(User, CustomUserAdmin)

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete contact messages
        return request.user.is_superuser
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    actions = ['mark_as_read', 'mark_as_unread']

admin.site.register(ContactMessage, ContactMessageAdmin)
