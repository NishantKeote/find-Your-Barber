from django.contrib import admin
from .models import (
    Shop, ServiceCategory, PredefinedService, ShopService,
    ShopPortfolioImage, ShopReview
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['display_name', 'name']


@admin.register(PredefinedService)
class PredefinedServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'estimated_duration', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


class ShopServiceInline(admin.TabularInline):
    model = ShopService
    extra = 0
    fields = ['predefined_service', 'custom_name', 'price', 'duration', 'is_available']


class ShopPortfolioImageInline(admin.TabularInline):
    model = ShopPortfolioImage
    extra = 0
    fields = ['image', 'title', 'service_category', 'is_featured']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'phone_number', 'is_active', 'get_average_rating']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'owner__username', 'description']
    inlines = [ShopServiceInline, ShopPortfolioImageInline]
    
    def get_average_rating(self, obj):
        avg = obj.get_average_rating()
        return f"{avg}★" if avg > 0 else "No ratings"
    get_average_rating.short_description = "Rating"


@admin.register(ShopService)
class ShopServiceAdmin(admin.ModelAdmin):
    list_display = ['shop', 'get_service_name', 'price', 'duration', 'is_available']
    list_filter = ['is_available', 'predefined_service__category']
    search_fields = ['shop__name', 'predefined_service__name', 'custom_name']
    
    def get_service_name(self, obj):
        return obj.name
    get_service_name.short_description = "Service Name"


@admin.register(ShopPortfolioImage)
class ShopPortfolioImageAdmin(admin.ModelAdmin):
    list_display = ['shop', 'title', 'service_category', 'is_featured', 'uploaded_at']
    list_filter = ['is_featured', 'service_category', 'uploaded_at']
    search_fields = ['shop__name', 'title', 'description']
    date_hierarchy = 'uploaded_at'


@admin.register(ShopReview)
class ShopReviewAdmin(admin.ModelAdmin):
    list_display = ['shop', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['shop__name', 'customer__username', 'review_text']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
