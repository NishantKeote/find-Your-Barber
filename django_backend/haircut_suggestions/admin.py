from django.contrib import admin
from .models import FaceShape, HaircutStyle, CustomerHaircutPhoto, HaircutSuggestion


@admin.register(FaceShape)
class FaceShapeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']


@admin.register(HaircutStyle)
class HaircutStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty_level', 'maintenance_level', 'is_active']
    list_filter = ['category', 'difficulty_level', 'maintenance_level', 'is_active']
    search_fields = ['name', 'description', 'tags']
    filter_horizontal = ['suitable_face_shapes']
    date_hierarchy = 'created_at'


@admin.register(CustomerHaircutPhoto)
class CustomerHaircutPhotoAdmin(admin.ModelAdmin):
    list_display = ['customer', 'detected_face_shape', 'confidence_score', 'upload_date']
    list_filter = ['detected_face_shape', 'upload_date']
    search_fields = ['customer__username']
    date_hierarchy = 'upload_date'
    readonly_fields = ['upload_date']


@admin.register(HaircutSuggestion)
class HaircutSuggestionAdmin(admin.ModelAdmin):
    list_display = ['customer_photo', 'haircut_style', 'match_score', 'created_at']
    list_filter = ['haircut_style__category', 'match_score', 'created_at']
    search_fields = ['customer_photo__customer__username', 'haircut_style__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
