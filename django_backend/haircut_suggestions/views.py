from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.templatetags.static import static as static_url
from .models import FaceShape, HaircutStyle, CustomerHaircutPhoto, HaircutSuggestion
from .ai.analysis import analyze_image, composite_overlay
from .ai.recommender import recommend, score_style
import os
import random


@login_required
def haircut_suggestions_view(request):
    """Main haircut suggestions page"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied')
        return redirect('shop_dashboard')
    
    # Get user's uploaded photos
    user_photos = CustomerHaircutPhoto.objects.filter(customer=request.user).order_by('-upload_date')
    
    # Get all face shapes for information
    face_shapes = FaceShape.objects.all()
    
    return render(request, 'haircut_suggestions/index.html', {
        'user_photos': user_photos,
        'face_shapes': face_shapes
    })


@login_required
@require_POST
def analyze_photo_view(request):
    """Analyze uploaded images and return haircut recommendations with previews."""
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)

    if 'front' not in request.FILES:
        return JsonResponse({'error': 'Front photo is required'}, status=400)

    front = request.FILES['front']
    side = request.FILES.get('side')
    gender = request.POST.get('gender', 'unisex')
    pref_length = request.POST.get('length') or None

    # Validate
    if front.size > 7 * 1024 * 1024:
        return JsonResponse({'error': 'Front photo size must be < 7MB'}, status=400)
    if not front.content_type.startswith('image/'):
        return JsonResponse({'error': 'Front file must be an image'}, status=400)
    if side and not side.content_type.startswith('image/'):
        return JsonResponse({'error': 'Side file must be an image'}, status=400)

    # Decode files early so corrupt uploads return a client error, not a 500.
    from PIL import Image
    try:
        front_img = Image.open(front)
        front_img.load()
        side_img = Image.open(side) if side else None
        if side_img:
            side_img.load()
    except (Image.UnidentifiedImageError, OSError, ValueError):
        return JsonResponse({'error': 'Please upload a valid image file'}, status=400)

    # Analyze and recommend
    try:
        result = analyze_image(front_img, side_img)
    except Exception:
        # Optional CV dependencies must not block catalogue recommendations.
        from .ai.analysis import AnalysisResult
        result = AnalysisResult(
            face_shape='oval', hair_type='straight', hair_length='medium',
            features={'confidence': 0.0, 'used_side_profile': bool(side_img), 'used_fallback': True},
            landmarks=None,
        )
    styles = recommend(result.face_shape, result.hair_type, pref_length or result.hair_length, gender)

    suggestions = []
    out_dir = os.path.join(settings.MEDIA_ROOT, 'suggestion_previews')
    os.makedirs(out_dir, exist_ok=True)

    for style in styles:
        preview_url = None
        match_score = score_style(style, result.face_shape, result.hair_type, pref_length or result.hair_length)
        try:
            if style.overlay_image:
                overlay_path = style.overlay_image.path
            else:
                overlay_path = None
            if overlay_path and os.path.isfile(overlay_path):
                from PIL import Image as PILImage
                ov = PILImage.open(overlay_path)
                composed = composite_overlay(front_img, ov, result.landmarks)
                filename = f"style_{style.id}_{request.user.id}.png"
                save_path = os.path.join(out_dir, filename)
                composed.save(save_path)
                preview_url = settings.MEDIA_URL + 'suggestion_previews/' + filename
            elif style.example_image:
                preview_url = style.example_image.url
        except Exception:
            if style.example_image:
                preview_url = style.example_image.url
        suggestions.append({
            'style_id': style.id,
            'name': style.name,
            'preview_url': preview_url,
            'match_score': match_score,
            'overlay_available': bool(getattr(style, 'overlay_image', None)),
        })

    return JsonResponse({
        'success': True,
        'face_shape': result.face_shape,
        'hair_type': result.hair_type,
        'hair_length': result.hair_length,
        'used_fallback': result.features.get('used_fallback', False),
        'suggestions': suggestions,
    })


@login_required
@require_POST
def upload_photo_view(request):
    """Handle photo upload for haircut suggestions"""
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if 'photo' not in request.FILES:
        return JsonResponse({'error': 'No photo uploaded'}, status=400)
    
    photo = request.FILES['photo']
    
    # Basic validation
    if photo.size > 5 * 1024 * 1024:  # 5MB limit
        return JsonResponse({'error': 'Photo size must be less than 5MB'}, status=400)
    
    if not photo.content_type.startswith('image/'):
        return JsonResponse({'error': 'File must be an image'}, status=400)
    
    # Create photo record
    customer_photo = CustomerHaircutPhoto.objects.create(
        customer=request.user,
        image=photo
    )
    
    # Simulate face shape detection (in production, use actual AI/ML service)
    face_shapes = FaceShape.objects.all()
    if face_shapes.exists():
        # For demo purposes, randomly assign a face shape with some confidence
        detected_shape = random.choice(face_shapes)
        customer_photo.detected_face_shape = detected_shape
        customer_photo.confidence_score = random.uniform(0.7, 0.95)
        customer_photo.save()
        
        # Generate suggestions based on detected face shape
        generate_suggestions(customer_photo)
    
    return JsonResponse({
        'success': True,
        'photo_id': customer_photo.id,
        'detected_shape': customer_photo.detected_face_shape.name if customer_photo.detected_face_shape else None,
        'confidence': customer_photo.confidence_score
    })


def generate_suggestions(customer_photo):
    """Generate haircut suggestions based on detected face shape"""
    if not customer_photo.detected_face_shape:
        return
    
    # Get suitable haircut styles for the detected face shape
    suitable_styles = HaircutStyle.objects.filter(
        suitable_face_shapes=customer_photo.detected_face_shape,
        is_active=True
    )
    
    # Create suggestions with match scores
    for style in suitable_styles:
        # Calculate match score based on confidence and other factors
        base_score = customer_photo.confidence_score * 0.8
        random_factor = random.uniform(0.1, 0.2)
        match_score = min(1.0, base_score + random_factor)
        
        # Generate reason for suggestion
        reason = f"This {style.name} works well with {customer_photo.detected_face_shape.get_name_display()} face shapes. "
        if style.maintenance_level == 'low':
            reason += "It's also low maintenance, making it perfect for busy lifestyles."
        elif style.difficulty_level == 'easy':
            reason += "It's easy to style and maintain."
        
        HaircutSuggestion.objects.create(
            customer_photo=customer_photo,
            haircut_style=style,
            match_score=match_score,
            reason=reason
        )


@login_required
def photo_suggestions_view(request, photo_id):
    """View suggestions for a specific uploaded photo"""
    if request.user.role != 'customer':
        messages.error(request, 'Access denied')
        return redirect('shop_dashboard')
    
    photo = get_object_or_404(CustomerHaircutPhoto, id=photo_id, customer=request.user)
    suggestions = HaircutSuggestion.objects.filter(customer_photo=photo).order_by('-match_score')
    
    return render(request, 'haircut_suggestions/photo_suggestions.html', {
        'photo': photo,
        'suggestions': suggestions
    })


@login_required
@require_POST
def delete_photo_view(request, photo_id):
    """Delete uploaded photo and its suggestions"""
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    photo = get_object_or_404(CustomerHaircutPhoto, id=photo_id, customer=request.user)
    
    # Delete the image file
    if photo.image and hasattr(photo.image, 'path'):
        import os
        if os.path.isfile(photo.image.path):
            os.remove(photo.image.path)
    
    photo.delete()
    
    return JsonResponse({'success': True})


def browse_styles_view(request):
    """Browse all available haircut styles in folder structure"""
    category_id = request.GET.get('category')
    
    from shops.models import ServiceCategory
    
    # If no category selected, show category folders
    if not category_id:
        categories = ServiceCategory.objects.filter(is_active=True)
        
        # Count styles in each category
        category_data = []
        for category in categories:
            style_count = HaircutStyle.objects.filter(
                category=category,
                is_active=True
            ).count()
            
            category_data.append({
                'category': category,
                'style_count': style_count,
                'icon': get_category_icon(category.name)
            })
        
        return render(request, 'haircut_suggestions/browse_categories.html', {
            'category_data': category_data,
        })
    
    # If category selected, show styles in that category
    else:
        try:
            category = ServiceCategory.objects.get(id=category_id, is_active=True)
            styles = HaircutStyle.objects.filter(
                category=category,
                is_active=True
            ).order_by('name')
            
            return render(request, 'haircut_suggestions/browse_styles.html', {
                'styles': styles,
                'category': category,
            })
        except ServiceCategory.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'Category not found')
            return redirect('browse_styles')


def get_category_icon(category_name):
    """Get appropriate icon for each category"""
    icons = {
        'haircut_men': 'fas fa-male',
        'haircut_women': 'fas fa-female',
        'beard': 'fas fa-user-tie',
        'spa_salon': 'fas fa-spa',
    }
    return icons.get(category_name, 'fas fa-cut')


@login_required
def style_detail_view(request, style_id):
    """View details of a specific haircut style"""
    style = get_object_or_404(HaircutStyle, id=style_id, is_active=True)
    
    # Find shops that offer similar services
    from shops.models import Shop, ShopService
    related_shops = Shop.objects.filter(
        is_active=True,
        services__predefined_service__category=style.category,
        services__is_available=True
    ).distinct()[:6]
    
    return render(request, 'haircut_suggestions/style_detail.html', {
        'style': style,
        'related_shops': related_shops
    })
