from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.shop_setup_view, name='shop_setup'),
    path('dashboard/', views.shop_dashboard_view, name='shop_dashboard'),
    path('list/', views.shop_list_view, name='shop_list'),
    path('<int:shop_id>/', views.shop_detail_view, name='shop_detail'),
    path('api/increase-waiting/', views.increase_waiting_count, name='increase_waiting_count'),
    path('api/decrease-waiting/', views.decrease_waiting_count, name='decrease_waiting_count'),
]