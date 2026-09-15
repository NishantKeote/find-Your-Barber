from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os

class User(AbstractUser):
    USER_ROLES = [
        ('customer', 'Customer'),
        ('shop_owner', 'Shop Owner'),
    ]
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def delete_account_data(self):
        """
        Delete all associated data before account deletion (GDPR compliant)
        """
        # Delete user's appointments
        self.appointments.all().delete()
        
        # Delete user's waiting list entries
        if hasattr(self, 'waiting_entries'):
            self.waiting_entries.all().delete()
        
        # Delete user's reviews
        if hasattr(self, 'reviews'):
            self.reviews.all().delete()
        
        # Delete user's uploaded haircut photos
        if hasattr(self, 'haircut_photos'):
            for photo in self.haircut_photos.all():
                if photo.image and os.path.isfile(photo.image.path):
                    os.remove(photo.image.path)
                photo.delete()
        
        # If user is a shop owner, delete shop and related data
        if self.role == 'shop_owner' and hasattr(self, 'shop'):
            shop = self.shop
            # Delete shop portfolio images
            if hasattr(shop, 'portfolio_images'):
                for img in shop.portfolio_images.all():
                    if img.image and os.path.isfile(img.image.path):
                        os.remove(img.image.path)
                    img.delete()
            
            # Delete shop services
            if hasattr(shop, 'custom_services'):
                shop.custom_services.all().delete()
            
            # Delete shop image
            if shop.image and os.path.isfile(shop.image.path):
                os.remove(shop.image.path)
            
            # Delete the shop itself
            shop.delete()
