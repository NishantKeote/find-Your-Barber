from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:shop_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('shop-appointments/', views.shop_appointments, name='shop_appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]