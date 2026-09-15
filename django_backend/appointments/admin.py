from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'shop', 'appointment_date', 'appointment_time',
        'status', 'total_price', 'total_duration'
    ]
    list_filter = ['status', 'appointment_date', 'shop']
    search_fields = ['customer__username', 'shop__name', 'special_request']
    date_hierarchy = 'appointment_date'
    filter_horizontal = ['services']
    readonly_fields = ['created_at', 'updated_at', 'total_price', 'total_duration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'shop', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Services', {
            'fields': ('services', 'total_price', 'total_duration')
        }),
        ('Notes & Requests', {
            'fields': ('special_request', 'service_description', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalculate totals when appointment is saved
        obj.calculate_totals()
