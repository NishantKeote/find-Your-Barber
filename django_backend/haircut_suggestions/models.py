from django.db import models
from django.contrib.auth import get_user_model
from shops.models import ServiceCategory

User = get_user_model()


class FaceShape(models.Model):
    """Face shape categories for haircut recommendations"""
    SHAPE_CHOICES = [
        ('round', 'Round'),
        ('oval', 'Oval'),
        ('square', 'Square'),
        ('heart', 'Heart'),
        ('oblong', 'Oblong'),
        ('diamond', 'Diamond'),
    ]
    
    name = models.CharField(max_length=20, choices=SHAPE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    characteristics = models.TextField(help_text="Key characteristics of this face shape")
    
    def __str__(self):
        return self.get_name_display()


class HaircutStyle(models.Model):
    """Recommended haircut styles"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='haircut_styles')
    description = models.TextField()
    suitable_face_shapes = models.ManyToManyField(FaceShape, related_name='suitable_haircuts')
    example_image = models.ImageField(upload_to='haircut_examples/', blank=True)
    overlay_image = models.ImageField(upload_to='style_overlays/', blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ], default='unisex')
    length_category = models.CharField(max_length=10, choices=[
        ('short', 'Short'),
        ('medium', 'Medium'),
        ('long', 'Long'),
        ('any', 'Any'),
    ], default='any')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='medium')
    maintenance_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.category.display_name})"
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class CustomerHaircutPhoto(models.Model):
    """Customer uploaded photos for haircut suggestions"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='haircut_photos')
    image = models.ImageField(upload_to='customer_photos/')
    detected_face_shape = models.ForeignKey(FaceShape, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in face shape detection")
    suggested_styles = models.ManyToManyField(HaircutStyle, through='HaircutSuggestion')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.username} - Photo {self.id}"
    
    class Meta:
        ordering = ['-upload_date']


class HaircutSuggestion(models.Model):
    """AI-generated haircut suggestions for customer photos"""
    customer_photo = models.ForeignKey(CustomerHaircutPhoto, on_delete=models.CASCADE)
    haircut_style = models.ForeignKey(HaircutStyle, on_delete=models.CASCADE)
    match_score = models.FloatField(help_text="How well this style matches the face shape")
    reason = models.TextField(blank=True, help_text="Why this style was suggested")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer_photo.customer.username} - {self.haircut_style.name} ({self.match_score:.1f})"
    
    class Meta:
        ordering = ['-match_score']
        unique_together = ['customer_photo', 'haircut_style']
