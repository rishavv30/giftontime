from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product_link', 'delivery_date', 'delivery_time', 'created_at')

