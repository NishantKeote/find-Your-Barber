from django.db import models
from django.contrib.auth import get_user_model
from shops.models import Shop, ShopService

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(ShopService, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    special_request = models.TextField(blank=True, help_text="Any special requests or notes")
    service_description = models.TextField(blank=True)  # Kept for backward compatibility
    notes = models.TextField(blank=True)  # Staff notes
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_duration = models.PositiveIntegerField(default=0, help_text="Total duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        
    def __str__(self):
        return f"{self.customer.username} - {self.shop.name} on {self.appointment_date}"
    
    def calculate_totals(self):
        """Calculate total price and duration from selected services"""
        total_price = sum(service.price for service in self.services.all())
        total_duration = sum(service.duration for service in self.services.all())
        
        self.total_price = total_price
        self.total_duration = total_duration
        self.save()
    
    def get_services_list(self):
        """Get comma-separated list of service names"""
        return ", ".join([service.name for service in self.services.all()])
