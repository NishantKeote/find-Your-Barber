from django.core.management.base import BaseCommand
from haircut_suggestions.models import FaceShape, HaircutStyle
from shops.models import ServiceCategory


class Command(BaseCommand):
    help = 'Populate the database with face shapes and haircut styles'

    def handle(self, *args, **options):
        # Create face shapes
        face_shapes_data = [
            {
                'name': 'round',
                'description': 'Round face shape with soft curves and similar width and length',
                'characteristics': 'Full cheeks, rounded chin, width and length are similar proportions'
            },
            {
                'name': 'oval',
                'description': 'Oval face shape, well-balanced proportions',
                'characteristics': 'Length is greater than width, forehead is slightly wider than chin'
            },
            {
                'name': 'square',
                'description': 'Square face shape with strong angular features',
                'characteristics': 'Strong jawline, wide forehead, angular features, width and length are similar'
            },
            {
                'name': 'heart',
                'description': 'Heart-shaped face with wider forehead and narrower chin',
                'characteristics': 'Wider forehead, high cheekbones, narrow pointed chin'
            },
            {
                'name': 'oblong',
                'description': 'Oblong face shape, longer than it is wide',
                'characteristics': 'Length is much greater than width, high forehead, long chin'
            },
            {
                'name': 'diamond',
                'description': 'Diamond face shape with narrow forehead and chin',
                'characteristics': 'Narrow forehead and chin, wide cheekbones, angular features'
            }
        ]

        self.stdout.write("Creating face shapes...")
        for shape_data in face_shapes_data:
            face_shape, created = FaceShape.objects.get_or_create(
                name=shape_data['name'],
                defaults=shape_data
            )
            if created:
                self.stdout.write(f"  ✓ Created face shape: {face_shape}")
            else:
                self.stdout.write(f"  - Face shape exists: {face_shape}")

        # Get service categories
        try:
            mens_category = ServiceCategory.objects.get(name='haircut_men')
            womens_category = ServiceCategory.objects.get(name='haircut_women')
            beard_category = ServiceCategory.objects.get(name='beard')
        except ServiceCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Service categories not found. Please run populate_services first.'))
            return

        # Create haircut styles for men
        mens_styles = [
            {
                'name': 'Crew Cut',
                'category': mens_category,
                'description': 'Short on sides and back, slightly longer on top',
                'suitable_face_shapes': ['oval', 'square', 'round'],
                'difficulty_level': 'easy',
                'maintenance_level': 'low',
                'tags': 'classic, easy to maintain, practical'
            },
            {
                'name': 'Undercut',
                'category': mens_category,
                'description': 'Sides shaved or faded, top longer',
                'suitable_face_shapes': ['oval', 'square'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'modern, versatile, edgy'
            },
            {
                'name': 'Pompadour',
                'category': mens_category,
                'description': 'Voluminous top, short sides',
                'suitable_face_shapes': ['oval', 'round'],
                'difficulty_level': 'hard',
                'maintenance_level': 'high',
                'tags': 'vintage, requires styling products, sophisticated'
            },
            {
                'name': 'Quiff',
                'category': mens_category,
                'description': 'Short sides, textured top brushed upwards',
                'suitable_face_shapes': ['oval', 'diamond'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'casual to formal style, textured, modern'
            },
            {
                'name': 'Buzz Cut',
                'category': mens_category,
                'description': 'Very short all over',
                'suitable_face_shapes': ['square', 'oval'],
                'difficulty_level': 'easy',
                'maintenance_level': 'low',
                'tags': 'minimal maintenance, simple, practical'
            },
            {
                'name': 'Fade',
                'category': mens_category,
                'description': 'Hair gradually shortens from top to bottom',
                'suitable_face_shapes': ['oval', 'square', 'round'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'can combine with other styles, versatile, modern'
            },
            {
                'name': 'Side Part',
                'category': mens_category,
                'description': 'Hair combed to one side',
                'suitable_face_shapes': ['oval', 'heart'],
                'difficulty_level': 'easy',
                'maintenance_level': 'low',
                'tags': 'professional look, classic, timeless'
            },
            {
                'name': 'Slick Back',
                'category': mens_category,
                'description': 'Hair brushed back smoothly',
                'suitable_face_shapes': ['oval', 'square'],
                'difficulty_level': 'medium',
                'maintenance_level': 'high',
                'tags': 'requires medium to long hair, sophisticated, formal'
            }
        ]

        # Create haircut styles for women
        womens_styles = [
            {
                'name': 'Bob Cut',
                'category': womens_category,
                'description': 'Classic chin-length cut. Perfect for adding structure to round faces.',
                'suitable_face_shapes': ['round', 'heart'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'classic, chic, timeless'
            },
            {
                'name': 'Pixie Cut',
                'category': womens_category,
                'description': 'Short and sassy cut. Great for highlighting facial features.',
                'suitable_face_shapes': ['oval', 'heart'],
                'difficulty_level': 'hard',
                'maintenance_level': 'high',
                'tags': 'bold, modern, low-maintenance'
            },
            {
                'name': 'Long Layers',
                'category': womens_category,
                'description': 'Flowing layers that add movement and soften angular features.',
                'suitable_face_shapes': ['square', 'diamond'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'feminine, flowing, versatile'
            },
            {
                'name': 'Lob (Long Bob)',
                'category': womens_category,
                'description': 'Shoulder-length bob that\'s versatile and modern.',
                'suitable_face_shapes': ['oval', 'square', 'oblong'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'modern, versatile, chic'
            },
            {
                'name': 'Face-Framing Layers',
                'category': womens_category,
                'description': 'Strategic layers that highlight your best features.',
                'suitable_face_shapes': ['round', 'square', 'diamond'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'flattering, customizable, feminine'
            }
        ]

        # Create beard styles
        beard_styles = [
            {
                'name': 'Stubble',
                'category': beard_category,
                'description': 'Short, evenly trimmed beard',
                'suitable_face_shapes': ['oval', 'square', 'round'],
                'difficulty_level': 'easy',
                'maintenance_level': 'low',
                'tags': 'low-maintenance, rugged look, casual'
            },
            {
                'name': 'Full Beard',
                'category': beard_category,
                'description': 'Thick, full beard covering jaw and cheeks',
                'suitable_face_shapes': ['oval', 'square'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'classic masculine style, traditional, distinguished'
            },
            {
                'name': 'Goatee',
                'category': beard_category,
                'description': 'Beard on chin only',
                'suitable_face_shapes': ['round', 'oval'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'adds definition to face, stylish, versatile'
            },
            {
                'name': 'Van Dyke',
                'category': beard_category,
                'description': 'Mustache with pointed chin beard',
                'suitable_face_shapes': ['oval', 'square'],
                'difficulty_level': 'hard',
                'maintenance_level': 'high',
                'tags': 'sophisticated, artistic style, requires precision'
            },
            {
                'name': 'Balbo',
                'category': beard_category,
                'description': 'Separate mustache and beard',
                'suitable_face_shapes': ['oval', 'square'],
                'difficulty_level': 'hard',
                'maintenance_level': 'high',
                'tags': 'modern, stylish, distinctive'
            },
            {
                'name': 'Chin Strap',
                'category': beard_category,
                'description': 'Thin line along jawline',
                'suitable_face_shapes': ['oval', 'square'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'highlights jaw structure, modern, clean'
            },
            {
                'name': 'Mutton Chops',
                'category': beard_category,
                'description': 'Sideburns extended along jawline',
                'suitable_face_shapes': ['square', 'oval'],
                'difficulty_level': 'medium',
                'maintenance_level': 'medium',
                'tags': 'vintage, bold, statement style'
            }
        ]

        all_styles = mens_styles + womens_styles + beard_styles

        self.stdout.write("\nCreating haircut styles...")
        total_created = 0

        for style_data in all_styles:
            suitable_shapes = style_data.pop('suitable_face_shapes')
            
            style, created = HaircutStyle.objects.get_or_create(
                name=style_data['name'],
                category=style_data['category'],
                defaults=style_data
            )
            
            if created:
                # Add suitable face shapes
                for shape_name in suitable_shapes:
                    try:
                        face_shape = FaceShape.objects.get(name=shape_name)
                        style.suitable_face_shapes.add(face_shape)
                    except FaceShape.DoesNotExist:
                        self.stdout.write(f"Warning: Face shape {shape_name} not found")
                
                self.stdout.write(f"  ✓ {style.name} ({style.category.display_name})")
                total_created += 1
            else:
                self.stdout.write(f"  - {style.name} (exists)")

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {total_created} new haircut styles!'))
        self.stdout.write("You can now use the AI haircut suggestion feature.")