from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Import your custom user model

# Optionally, you can create a custom UserAdmin class to customize how users are displayed
class CustomUserAdmin(UserAdmin):
    # Specify any additional fields or customizations here
    # Example: add a field to the list display in admin
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')  # Customize list_filter
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ()  # Remove `groups` and `user_permissions` references

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
