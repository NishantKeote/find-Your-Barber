from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from .models import WaitingListEntry
from shops.models import Shop
from datetime import timedelta

@login_required
@require_POST
def join_waiting_list(request, shop_id):
    """Customer joins waiting list for a shop"""
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Only customers can join waiting list'}, status=403)
    
    shop = get_object_or_404(Shop, id=shop_id, is_active=True)
    
    # Check if user is already in waiting list
    existing_entry = WaitingListEntry.objects.filter(
        customer=request.user,
        shop=shop,
        status='waiting'
    ).first()
    
    if existing_entry:
        return JsonResponse({'error': 'You are already in the waiting list'}, status=400)
    
    # Check if shop has space
    if shop.current_waiting_count >= shop.max_waiting_list_size:
        return JsonResponse({'error': 'Waiting list is full'}, status=400)
    
    # Get next position number
    last_entry = WaitingListEntry.objects.filter(
        shop=shop,
        status='waiting'
    ).order_by('-position_number').first()
    
    next_position = (last_entry.position_number + 1) if last_entry else 1
    
    # Create waiting list entry
    entry = WaitingListEntry.objects.create(
        customer=request.user,
        shop=shop,
        position_number=next_position,
        estimated_wait_time=timedelta(minutes=next_position * 15)  # Estimate 15 min per person
    )
    
    # Update shop waiting count
    shop.increase_waiting_count()
    
    return JsonResponse({
        'success': True,
        'position': entry.position_number,
        'estimated_wait_minutes': entry.estimated_wait_time.total_seconds() // 60 if entry.estimated_wait_time else None
    })

@login_required
@require_POST
def leave_waiting_list(request, entry_id):
    """Customer leaves waiting list"""
    entry = get_object_or_404(WaitingListEntry, id=entry_id, customer=request.user, status='waiting')
    
    # Update entry status
    entry.status = 'left'
    entry.save()
    
    # Update shop waiting count
    entry.shop.decrease_waiting_count()
    
    # Update position numbers for remaining entries
    WaitingListEntry.objects.filter(
        shop=entry.shop,
        status='waiting',
        position_number__gt=entry.position_number
    ).update(position_number=models.F('position_number') - 1)
    
    return JsonResponse({'success': True})

@login_required
def my_waiting_lists(request):
    """View user's current waiting list entries"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied')
        return redirect('shop_dashboard')
    
    waiting_entries = request.user.waiting_entries.filter(status='waiting')
    
    return render(request, 'waiting_lists/my_lists.html', {
        'waiting_entries': waiting_entries
    })
