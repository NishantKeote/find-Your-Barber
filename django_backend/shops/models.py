from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Shop(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone_number = models.CharField(max_length=15)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    max_waiting_list_size = models.PositiveIntegerField(default=20)
    current_waiting_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='shop_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def increase_waiting_count(self):
        if self.current_waiting_count < self.max_waiting_list_size:
            self.current_waiting_count += 1
            self.save()
            return True
        return False
    
    def decrease_waiting_count(self):
        if self.current_waiting_count > 0:
            self.current_waiting_count -= 1
            self.save()
            return True
        return False
