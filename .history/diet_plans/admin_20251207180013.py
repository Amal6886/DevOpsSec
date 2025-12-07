from django.contrib import admin
from .models import DietPlan


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_type', 'daily_calories', 'created_at']
    list_filter = ['goal_type', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
