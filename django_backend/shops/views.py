from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Shop
from waiting_lists.models import WaitingListEntry
from appointments.models import Appointment
from geopy.distance import geodesic
import json

@login_required
def shop_setup_view(request):
    if request.user.role != 'shop_owner':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if hasattr(request.user, 'shop'):
        return redirect('shop_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        opening_time = request.POST.get('opening_time')
        closing_time = request.POST.get('closing_time')
        max_waiting_list_size = int(request.POST.get('max_waiting_list_size', 20))
        
        # For now, we'll use dummy coordinates - in production, use geocoding
        latitude = float(request.POST.get('latitude', 0))
        longitude = float(request.POST.get('longitude', 0))
        
        shop = Shop.objects.create(
            owner=request.user,
            name=name,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude,
            phone_number=phone_number,
            opening_time=opening_time,
            closing_time=closing_time,
            max_waiting_list_size=max_waiting_list_size
        )
        
        messages.success(request, 'Shop registered successfully!')
        return redirect('shop_dashboard')
    
    return render(request, 'shops/setup.html')

@login_required
def shop_dashboard_view(request):
    if request.user.role != 'shop_owner':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if not hasattr(request.user, 'shop'):
        return redirect('shop_setup')
    
    shop = request.user.shop
    waiting_list = shop.waiting_list.filter(status='waiting').order_by('position_number')
    recent_appointments = shop.appointments.all()[:10]
    
    return render(request, 'shops/dashboard.html', {
        'shop': shop,
        'waiting_list': waiting_list,
        'recent_appointments': recent_appointments
    })

@login_required
@require_POST
def increase_waiting_count(request):
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    shop = request.user.shop
    if shop.increase_waiting_count():
        return JsonResponse({
            'success': True,
            'current_count': shop.current_waiting_count,
            'max_count': shop.max_waiting_list_size
        })
    else:
        return JsonResponse({'error': 'Maximum waiting list size reached'}, status=400)

@login_required
@require_POST
def decrease_waiting_count(request):
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    shop = request.user.shop
    if shop.decrease_waiting_count():
        return JsonResponse({
            'success': True,
            'current_count': shop.current_waiting_count,
            'max_count': shop.max_waiting_list_size
        })
    else:
        return JsonResponse({'error': 'No customers in waiting list'}, status=400)

@login_required
def shop_list_view(request):
    """View for customers to see nearby shops"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied')
        return redirect('shop_dashboard')
    
    query = request.GET.get('q', '')
    shops = Shop.objects.filter(is_active=True)
    
    if query:
        shops = shops.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )
    
    # In production, you would calculate distance based on user location
    shops_with_distance = []
    for shop in shops:
        shops_with_distance.append({
            'shop': shop,
            'distance': 'N/A'  # Calculate real distance in production
        })
    
    return render(request, 'shops/list.html', {
        'shops_with_distance': shops_with_distance,
        'query': query
    })

@login_required
def shop_detail_view(request, shop_id):
    """View for customers to see shop details and join waiting list"""
    shop = get_object_or_404(Shop, id=shop_id, is_active=True)
    
    # Check if user is already in waiting list
    user_in_waiting = None
    if request.user.is_authenticated and request.user.role == 'customer':
        user_in_waiting = WaitingListEntry.objects.filter(
            customer=request.user,
            shop=shop,
            status='waiting'
        ).first()
    
    return render(request, 'shops/detail.html', {
        'shop': shop,
        'user_in_waiting': user_in_waiting,
        'waiting_count': shop.current_waiting_count
    })
