from django.urls import path
from . import views

urlpatterns = [
    path('join/<int:shop_id>/', views.join_waiting_list, name='join_waiting_list'),
    path('leave/<int:entry_id>/', views.leave_waiting_list, name='leave_waiting_list'),
    path('my-waiting-lists/', views.my_waiting_lists, name='my_waiting_lists'),
]