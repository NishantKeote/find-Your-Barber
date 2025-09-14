from django.db import models
from django.contrib.auth import get_user_model
from shops.models import Shop

User = get_user_model()

class WaitingListEntry(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('served', 'Served'),
        ('left', 'Left'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waiting_entries')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='waiting_list')
    position_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    joined_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    estimated_wait_time = models.DurationField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['position_number']
        unique_together = ['shop', 'position_number', 'status']
        
    def __str__(self):
        return f"{self.customer.username} - Position {self.position_number} at {self.shop.name}"
