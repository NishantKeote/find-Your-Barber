from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

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
    
    def get_average_rating(self):
        """Calculate average rating for this shop"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0


class ServiceCategory(models.Model):
    """Categories for barber services"""
    CATEGORY_CHOICES = [
        ('haircut_men', 'Men\'s Haircuts'),
        ('haircut_women', 'Women\'s Haircuts'),
        ('beard', 'Beard Styles'),
        ('spa_salon', 'Spa & Salon Services'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name
    
    class Meta:
        verbose_name_plural = "Service Categories"


class PredefinedService(models.Model):
    """Predefined services that shops can choose from"""
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='predefined_services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.display_name} - {self.name}"
    
    class Meta:
        unique_together = ['category', 'name']


class ShopService(models.Model):
    """Services offered by a specific shop with pricing"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='services')
    predefined_service = models.ForeignKey(PredefinedService, on_delete=models.CASCADE, null=True, blank=True)
    custom_name = models.CharField(max_length=100, blank=True, help_text="For custom services")
    custom_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.predefined_service:
            return f"{self.shop.name} - {self.predefined_service.name} (Rs.{self.price})"
        return f"{self.shop.name} - {self.custom_name} (Rs.{self.price})"
    
    @property
    def name(self):
        return self.custom_name if self.custom_name else self.predefined_service.name
    
    @property
    def description(self):
        return self.custom_description if self.custom_description else (self.predefined_service.description if self.predefined_service else "")
    
    class Meta:
        unique_together = ['shop', 'predefined_service', 'custom_name']


class ShopPortfolioImage(models.Model):
    """Portfolio images for barbershops"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='portfolio_images')
    image = models.ImageField(upload_to='portfolio_images/')
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.shop.name} - {self.title or 'Portfolio Image'}"
    
    class Meta:
        ordering = ['-is_featured', '-uploaded_at']


class ShopReview(models.Model):
    """Customer reviews for shops"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.username} - {self.shop.name} ({self.rating}★)"
    
    class Meta:
        unique_together = ['shop', 'customer']  # One review per customer per shop
        ordering = ['-created_at']
