from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import (
    Shop, ServiceCategory, PredefinedService, ShopService,
    ShopPortfolioImage, ShopReview
)
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

def shop_detail_view(request, shop_id):
    """View for customers to see shop details and join waiting list"""
    shop = get_object_or_404(Shop, id=shop_id, is_active=True)
    
    # Check if user is already in waiting list
    user_in_waiting = None
    user_can_review = False
    user_has_appointment = False
    user_existing_review = None
    
    if request.user.is_authenticated and request.user.role == 'customer':
        user_in_waiting = WaitingListEntry.objects.filter(
            customer=request.user,
            shop=shop,
            status='waiting'
        ).first()
        
        # Check if user has completed appointments at this shop
        completed_appointments = Appointment.objects.filter(
            customer=request.user,
            shop=shop,
            status='completed'
        ).exists()
        
        # Check if user has any appointment at this shop
        user_has_appointment = Appointment.objects.filter(
            customer=request.user,
            shop=shop
        ).exists()
        
        user_can_review = completed_appointments
        
        # Check if user has already reviewed this shop
        user_existing_review = ShopReview.objects.filter(
            customer=request.user,
            shop=shop
        ).first()
    
    # Get shop reviews and services
    reviews = shop.reviews.all().order_by('-created_at')[:10]
    services = shop.services.filter(is_available=True)
    portfolio_images = shop.portfolio_images.all()[:8]
    
    return render(request, 'shops/detail.html', {
        'shop': shop,
        'user_in_waiting': user_in_waiting,
        'waiting_count': shop.current_waiting_count,
        'reviews': reviews,
        'services': services,
        'portfolio_images': portfolio_images,
        'average_rating': shop.get_average_rating(),
        'total_reviews': shop.reviews.count(),
        'user_can_review': user_can_review,
        'user_has_appointment': user_has_appointment,
        'user_existing_review': user_existing_review
    })


@login_required
def manage_services_view(request):
    """Shop owner can manage their services"""
    if request.user.role != 'shop_owner':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if not hasattr(request.user, 'shop'):
        return redirect('shop_setup')
    
    shop = request.user.shop
    
    if request.method == 'POST':
        # Add new service
        predefined_service_id = request.POST.get('predefined_service')
        custom_name = request.POST.get('custom_name')
        custom_description = request.POST.get('custom_description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        
        if predefined_service_id:
            predefined_service = get_object_or_404(PredefinedService, id=predefined_service_id)
            shop_service = ShopService.objects.create(
                shop=shop,
                predefined_service=predefined_service,
                price=price,
                duration=duration or predefined_service.estimated_duration
            )
        elif custom_name:
            shop_service = ShopService.objects.create(
                shop=shop,
                custom_name=custom_name,
                custom_description=custom_description,
                price=price,
                duration=duration
            )
        else:
            messages.error(request, 'Please select a predefined service or enter a custom service name.')
            return redirect('manage_services')
        
        messages.success(request, 'Service added successfully!')
        return redirect('manage_services')
    
    # Get all service categories and predefined services
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('predefined_services')
    shop_services = shop.services.all().order_by('predefined_service__category__name')
    
    return render(request, 'shops/manage_services.html', {
        'shop': shop,
        'categories': categories,
        'shop_services': shop_services
    })


@login_required
@require_POST
def toggle_service_availability(request, service_id):
    """Toggle service availability"""
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    service = get_object_or_404(ShopService, id=service_id, shop__owner=request.user)
    service.is_available = not service.is_available
    service.save()
    
    return JsonResponse({
        'success': True,
        'is_available': service.is_available
    })


@login_required
@require_POST
def delete_service(request, service_id):
    """Delete a shop service"""
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    service = get_object_or_404(ShopService, id=service_id, shop__owner=request.user)
    service.delete()
    
    messages.success(request, 'Service deleted successfully!')
    return JsonResponse({'success': True})


@login_required
def manage_portfolio_view(request):
    """Shop owner can manage their portfolio images"""
    if request.user.role != 'shop_owner':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if not hasattr(request.user, 'shop'):
        return redirect('shop_setup')
    
    shop = request.user.shop
    
    if request.method == 'POST':
        # Upload new portfolio image
        image = request.FILES.get('image')
        title = request.POST.get('title')
        description = request.POST.get('description')
        service_category_id = request.POST.get('service_category')
        is_featured = request.POST.get('is_featured') == 'on'
        
        if image:
            portfolio_image = ShopPortfolioImage.objects.create(
                shop=shop,
                image=image,
                title=title,
                description=description,
                is_featured=is_featured
            )
            
            if service_category_id:
                portfolio_image.service_category = get_object_or_404(ServiceCategory, id=service_category_id)
                portfolio_image.save()
            
            messages.success(request, 'Portfolio image uploaded successfully!')
        else:
            messages.error(request, 'Please select an image to upload.')
        
        return redirect('manage_portfolio')
    
    portfolio_images = shop.portfolio_images.all().order_by('-is_featured', '-uploaded_at')
    categories = ServiceCategory.objects.filter(is_active=True)
    
    return render(request, 'shops/manage_portfolio.html', {
        'shop': shop,
        'portfolio_images': portfolio_images,
        'categories': categories
    })


@login_required
@require_POST
def delete_portfolio_image(request, image_id):
    """Delete a portfolio image"""
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    image = get_object_or_404(ShopPortfolioImage, id=image_id, shop__owner=request.user)
    
    # Delete the actual image file
    if image.image and hasattr(image.image, 'path'):
        import os
        if os.path.isfile(image.image.path):
            os.remove(image.image.path)
    
    image.delete()
    
    messages.success(request, 'Portfolio image deleted successfully!')
    return JsonResponse({'success': True})


@login_required
@require_POST
def submit_review(request, shop_id):
    """Customer can submit a review for a shop"""
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Only customers can submit reviews'}, status=403)
    
    shop = get_object_or_404(Shop, id=shop_id)
    
    # Check if customer has completed at least one appointment with this shop
    completed_appointments = Appointment.objects.filter(
        customer=request.user,
        shop=shop,
        status='completed'
    ).exists()
    
    if not completed_appointments:
        return JsonResponse({'error': 'You can only review shops where you have completed appointments'}, status=400)
    
    # Check if customer has already reviewed this shop
    existing_review = ShopReview.objects.filter(customer=request.user, shop=shop).first()
    
    rating = int(request.POST.get('rating', 0))
    review_text = request.POST.get('review_text', '').strip()
    
    if not (1 <= rating <= 5):
        return JsonResponse({'error': 'Rating must be between 1 and 5 stars'}, status=400)
    
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.review_text = review_text
        existing_review.save()
        messages.success(request, 'Your review has been updated!')
    else:
        # Create new review
        ShopReview.objects.create(
            shop=shop,
            customer=request.user,
            rating=rating,
            review_text=review_text
        )
        messages.success(request, 'Thank you for your review!')
    
    return JsonResponse({
        'success': True,
        'new_average': shop.get_average_rating(),
        'total_reviews': shop.reviews.count()
    })
