
from django.contrib import admin
from .models import Shop

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'phone', 'email', 'address')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Address', {
            'fields': ('address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )