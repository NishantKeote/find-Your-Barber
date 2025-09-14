from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:shop_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('shop-appointments/', views.shop_appointments, name='shop_appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    # Shop owner appointment actions
    path('start/<int:appointment_id>/', views.start_appointment, name='start_appointment'),
    path('complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('cancel-by-shop/<int:appointment_id>/', views.cancel_appointment_by_shop, name='cancel_appointment_by_shop'),
]
