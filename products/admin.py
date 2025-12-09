from django.contrib import admin
from .models import Supplement, ProteinBar


@admin.register(Supplement)
class SupplementAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'stock_quantity', 'threshold', 'is_low_stock', 'created_at']
    list_filter = ['brand', 'category', 'created_at']
    search_fields = ['name', 'brand', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(ProteinBar)
class ProteinBarAdmin(admin.ModelAdmin):
    list_display = ['name', 'flavor', 'price', 'stock_quantity', 'threshold', 'is_low_stock', 'created_at']
    list_filter = ['flavor', 'created_at']
    search_fields = ['name', 'flavor', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'
