from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, Product, Customer, Sale, SaleItem, 
    Discount, Inventory
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'product_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'sku', 'price', 'stock_quantity', 
        'stock_status', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['price', 'stock_quantity', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'sku', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'min_stock_level')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        if obj.is_low_stock:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">Low Stock</span>'
            )
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">In Stock</span>'
        )
    stock_status.short_description = 'Stock Status'

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['total_price']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        'sale_number', 'customer', 'cashier', 'total_items',
        'final_amount', 'payment_method', 'created_at'
    ]
    list_filter = ['payment_method', 'created_at', 'cashier']
    search_fields = ['sale_number', 'customer__name']
    readonly_fields = [
        'sale_number', 'total_amount', 'discount_amount', 
        'tax_amount', 'final_amount', 'change_given', 'created_at'
    ]
    inlines = [SaleItemInline]
    
    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Items'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['cashier', 'customer']
        return self.readonly_fields

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'phone', 'loyalty_tier', 
        'loyalty_points', 'total_spent', 'total_purchases', 'created_at'
    ]
    list_filter = ['loyalty_tier', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['total_spent', 'created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Loyalty Program', {
            'fields': ('loyalty_tier', 'loyalty_points', 'total_spent')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def total_purchases(self, obj):
        return obj.sale_set.count()
    total_purchases.short_description = 'Total Purchases'

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'percentage', 'minimum_amount', 
        'valid_from', 'valid_to', 'is_active', 'status'
    ]
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['name', 'description']
    
    def status(self, obj):
        if obj.is_valid:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">Active</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">Expired</span>'
        )
    status.short_description = 'Status'

from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "checkout_request_id",
        "sale",
        "phone_number",
        "amount",
        "status",
        "mpesa_receipt",
        "transaction_date",
        "created_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = (
        "checkout_request_id",
        "phone_number",
        "mpesa_receipt",
        "sale__id",
    )
    readonly_fields = ("created_at", "updated_at", "raw_response")

    fieldsets = (
        ("Payment Details", {
            "fields": (
                "sale",
                "checkout_request_id",
                "status",
                "phone_number",
                "amount",
                "mpesa_receipt",
                "transaction_date",
            )
        }),
        ("M-Pesa Response", {
            "classes": ("collapse",),
            "fields": ("raw_response",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    ordering = ("-created_at",)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'transaction_type', 'quantity', 
        'user', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at', 'user']
    search_fields = ['product__name', 'notes']
    readonly_fields = ['created_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['product', 'transaction_type', 'quantity', 'user']
        return self.readonly_fields