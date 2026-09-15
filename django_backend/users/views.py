from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from .models import User
from shops.models import Shop

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'customer')
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'users/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone_number=phone_number,
            address=address
        )
        
        login(request, user)
        messages.success(request, 'Registration successful!')
        
        if role == 'shop_owner':
            return redirect('shop_setup')
        else:
            return redirect('dashboard')
    
    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            if user.role == 'shop_owner':
                return redirect('shop_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.role == 'shop_owner':
        return redirect('shop_dashboard')
    
    # Get recently visited shops based on appointments and waiting list entries
    visited_shops = []
    
    # Get shops from recent appointments
    recent_appointments = request.user.appointments.all().order_by('-created_at')[:10]
    for appointment in recent_appointments:
        if appointment.shop not in visited_shops:
            visited_shops.append(appointment.shop)
    
    # Get shops from recent waiting list entries
    if hasattr(request.user, 'waiting_entries'):
        recent_waiting = request.user.waiting_entries.all().order_by('-joined_at')[:10]
        for entry in recent_waiting:
            if entry.shop not in visited_shops:
                visited_shops.append(entry.shop)
    
    # Limit to 3 most recent shops
    recently_visited_shops = visited_shops[:3]
    
    # Get recommended shops based on user's choices and preferences
    recommended_shops = []
    
    # Get services from user's appointments to understand preferences
    user_service_categories = set()
    user_appointments = request.user.appointments.all()
    
    for appointment in user_appointments:
        for service in appointment.services.all():
            if service.predefined_service and service.predefined_service.category:
                user_service_categories.add(service.predefined_service.category.name)
    
    # If user has service preferences, recommend shops with those services
    if user_service_categories:
        from shops.models import ShopService
        recommended_shop_ids = ShopService.objects.filter(
            predefined_service__category__name__in=user_service_categories,
            is_available=True,
            shop__is_active=True
        ).exclude(
            shop__in=visited_shops  # Exclude already visited shops
        ).values_list('shop_id', flat=True).distinct()
        
        recommended_shops = Shop.objects.filter(
            id__in=recommended_shop_ids
        ).order_by('-id')[:3]  # Get 3 newest shops with preferred services
    
    # If no preferences or no matching shops, recommend highest rated shops
    if not recommended_shops or (hasattr(recommended_shops, 'exists') and not recommended_shops.exists()) or len(recommended_shops) == 0:
        # Get shops with good ratings, excluding visited ones
        all_shops = Shop.objects.filter(is_active=True)
        if visited_shops:
            all_shops = all_shops.exclude(id__in=[shop.id for shop in visited_shops])
        
        # Sort by average rating (this is a simple approach)
        recommended_shops = sorted(
            all_shops[:10],  # Limit to avoid performance issues
            key=lambda shop: shop.get_average_rating() or 0,
            reverse=True
        )[:3]
    
    # Customer dashboard
    return render(request, 'users/dashboard.html', {
        'user': request.user,
        'appointments': request.user.appointments.all()[:5],
        'waiting_entries': request.user.waiting_entries.filter(status='waiting')[:5],
        'recently_visited_shops': recently_visited_shops,
        'recommended_shops': recommended_shops
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
@require_POST
def delete_account_view(request):
    """
    Delete user account and all associated data
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        
        # Verify password before deletion
        user = authenticate(request, username=request.user.username, password=password)
        if user is None:
            messages.error(request, 'Incorrect password. Account deletion cancelled.')
            return redirect('profile')
        
        try:
            # Delete all associated data
            user.delete_account_data()
            
            # Log out the user
            logout(request)
            
            # Delete the user account
            user.delete()
            
            messages.success(request, 'Your account has been permanently deleted. Thank you for using our service.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'An error occurred while deleting your account: {str(e)}')
            return redirect('profile')
    
    return redirect('profile')
