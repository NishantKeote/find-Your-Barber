from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Appointment
from shops.models import Shop, ShopService
from datetime import datetime, date, timedelta
import json

@login_required
def book_appointment(request, shop_id):
    """Customer books appointment at a shop"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can book appointments')
        return redirect('shop_dashboard')
    
    shop = get_object_or_404(Shop, id=shop_id, is_active=True)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        selected_services = request.POST.getlist('services')  # Multiple services
        special_request = request.POST.get('special_request', '')
        service_description = request.POST.get('service_description', '')  # Legacy field
        notes = request.POST.get('notes', '')
        
        try:
            # Parse date and time
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
            
            # Check if appointment is in the future
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            appointment_datetime = timezone.make_aware(appointment_datetime)
            if appointment_datetime <= timezone.now():
                messages.error(request, 'Appointment must be in the future')
                return render(request, 'appointments/book.html', {'shop': shop})
            
            # Check for existing appointments at the same time
            existing_appointment = Appointment.objects.filter(
                shop=shop,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['scheduled', 'in_progress']
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'This time slot is already booked')
                return render(request, 'appointments/book.html', {'shop': shop})
            
            # Validate selected services
            if not selected_services:
                messages.error(request, 'Please select at least one service')
                return render(request, 'appointments/book.html', {
                    'shop': shop,
                    'services': shop.services.filter(is_available=True)
                })
            
            # Verify services belong to this shop
            services = ShopService.objects.filter(
                id__in=selected_services,
                shop=shop,
                is_available=True
            )
            
            if len(services) != len(selected_services):
                messages.error(request, 'Invalid service selection')
                return render(request, 'appointments/book.html', {
                    'shop': shop,
                    'services': shop.services.filter(is_available=True)
                })
            
            # Create appointment
            appointment = Appointment.objects.create(
                customer=request.user,
                shop=shop,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                special_request=special_request,
                service_description=service_description,
                notes=notes
            )
            
            # Add selected services to appointment
            appointment.services.set(services)
            
            # Calculate totals
            appointment.calculate_totals()
            
            messages.success(request, f'Appointment booked successfully for {appointment_date} at {appointment_time}')
            return redirect('my_appointments')
            
        except ValueError:
            messages.error(request, 'Invalid date or time format')
    
    # Get available services for this shop
    services = shop.services.filter(is_available=True).select_related('predefined_service__category')
    
    return render(request, 'appointments/book.html', {
        'shop': shop,
        'services': services
    })

@login_required
def my_appointments(request):
    """View user's appointments"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied')
        return redirect('shop_dashboard')
    
    appointments = request.user.appointments.all().order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })

@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user)
    
    if appointment.status not in ['scheduled']:
        return JsonResponse({'error': 'Cannot cancel this appointment'}, status=400)
    
    appointment.status = 'cancelled'
    appointment.save()
    
    return JsonResponse({'success': True})

@login_required
def shop_appointments(request):
    """Shop owner view of appointments"""
    if request.user.role != 'shop_owner':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if not hasattr(request.user, 'shop'):
        messages.error(request, 'Please set up your shop first')
        return redirect('shop_setup')
    
    shop = request.user.shop
    appointments = shop.appointments.all().order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'appointments/shop_appointments.html', {
        'appointments': appointments,
        'shop': shop
    })

@login_required
@require_POST
def start_appointment(request, appointment_id):
    """Shop owner starts an appointment (mark as in progress)"""
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get appointment for this shop owner
    appointment = get_object_or_404(Appointment, 
                                  id=appointment_id, 
                                  shop__owner=request.user)
    
    if appointment.status != 'scheduled':
        return JsonResponse({'error': 'Can only start scheduled appointments'}, status=400)
    
    appointment.status = 'in_progress'
    appointment.save()
    
    return JsonResponse({
        'success': True, 
        'message': 'Appointment started successfully',
        'new_status': 'in_progress'
    })

@login_required
@require_POST
def complete_appointment(request, appointment_id):
    """Shop owner completes an appointment"""
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get appointment for this shop owner
    appointment = get_object_or_404(Appointment, 
                                  id=appointment_id, 
                                  shop__owner=request.user)
    
    if appointment.status not in ['scheduled', 'in_progress']:
        return JsonResponse({'error': 'Can only complete scheduled or in-progress appointments'}, status=400)
    
    appointment.status = 'completed'
    appointment.save()
    
    return JsonResponse({
        'success': True, 
        'message': 'Appointment completed successfully',
        'new_status': 'completed'
    })

@login_required
@require_POST
def cancel_appointment_by_shop(request, appointment_id):
    """Shop owner cancels an appointment"""
    if request.user.role != 'shop_owner':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get appointment for this shop owner
    appointment = get_object_or_404(Appointment, 
                                  id=appointment_id, 
                                  shop__owner=request.user)
    
    if appointment.status not in ['scheduled', 'in_progress']:
        return JsonResponse({'error': 'Can only cancel scheduled or in-progress appointments'}, status=400)
    
    appointment.status = 'cancelled'
    appointment.save()
    
    return JsonResponse({
        'success': True, 
        'message': 'Appointment cancelled successfully',
        'new_status': 'cancelled'
    })
