from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'location', 'is_active', 'is_staff']
    list_filter = ['role', 'location', 'is_active', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('KMUTNB Shop Role & Location', {'fields': ('role', 'location')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('KMUTNB Shop Role & Location', {'fields': ('role', 'location')}),
    )
