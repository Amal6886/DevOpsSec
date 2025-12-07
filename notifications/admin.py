from django.contrib import admin
from .models import StockAlert


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_sent', 'alert_date', 'message']
    list_filter = ['alert_sent', 'alert_date']
    readonly_fields = ['content_type', 'object_id', 'product', 'alert_date', 'message']
    search_fields = ['message']
