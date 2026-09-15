from django.urls import path
from . import views

urlpatterns = [
    path('', views.haircut_suggestions_view, name='haircut_suggestions'),
    path('analyze/', views.analyze_photo_view, name='analyze_haircut_ai'),
    path('upload/', views.upload_photo_view, name='upload_photo'),
    path('photo/<int:photo_id>/', views.photo_suggestions_view, name='photo_suggestions'),
    path('delete-photo/<int:photo_id>/', views.delete_photo_view, name='delete_photo'),
    path('browse-styles/', views.browse_styles_view, name='browse_styles'),
    path('style/<int:style_id>/', views.style_detail_view, name='style_detail'),
]
