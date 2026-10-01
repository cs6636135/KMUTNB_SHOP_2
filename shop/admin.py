from django.contrib import admin
from .models import Category, Product, Location, Stock

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'building', 'floor', 'room']
    search_fields = ['name', 'building']

class StockInline(admin.TabularInline):
    model = Stock
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price', 'reservable', 'total_stock', 'created_at']
    list_filter = ['category', 'reservable', 'created_at']
    search_fields = ['name', 'description']
    inlines = [StockInline]

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'location', 'stock']
    list_filter = ['location', 'product__category']
    search_fields = ['product__name', 'location__name']
