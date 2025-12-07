from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone', 'is_customer', 'is_staff', 'date_joined']
    list_filter = ['is_customer', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'is_customer')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'fitness_goal', 'current_weight', 'target_weight']
    list_filter = ['fitness_goal', 'gender', 'activity_level']
    search_fields = ['user__username', 'user__email']
