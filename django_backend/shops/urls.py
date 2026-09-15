from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.shop_setup_view, name='shop_setup'),
    path('dashboard/', views.shop_dashboard_view, name='shop_dashboard'),
    path('list/', views.shop_list_view, name='shop_list'),
    path('<int:shop_id>/', views.shop_detail_view, name='shop_detail'),
    path('api/increase-waiting/', views.increase_waiting_count, name='increase_waiting_count'),
    path('api/decrease-waiting/', views.decrease_waiting_count, name='decrease_waiting_count'),
    
    # Services management
    path('manage/services/', views.manage_services_view, name='manage_services'),
    path('api/toggle-service/<int:service_id>/', views.toggle_service_availability, name='toggle_service_availability'),
    path('api/delete-service/<int:service_id>/', views.delete_service, name='delete_service'),
    
    # Portfolio management
    path('manage/portfolio/', views.manage_portfolio_view, name='manage_portfolio'),
    path('api/delete-portfolio-image/<int:image_id>/', views.delete_portfolio_image, name='delete_portfolio_image'),
    
    # Reviews
    path('api/submit-review/<int:shop_id>/', views.submit_review, name='submit_review'),
]
