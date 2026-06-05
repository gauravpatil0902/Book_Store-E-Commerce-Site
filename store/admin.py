from django.contrib import admin

from .models import CustomerProfile, Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "price"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "rating", "in_stock"]
    search_fields = ["title"]
    list_filter = ["rating", "in_stock"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "contact_number", "city", "state", "pincode"]
    search_fields = ["user__username", "user__first_name", "user__email", "contact_number"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "contact_number", "total", "status", "order_date", "delivery_date"]
    list_filter = ["status", "order_date", "delivery_date"]
    inlines = [OrderItemInline]
