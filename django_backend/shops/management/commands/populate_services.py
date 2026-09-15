from django.core.management.base import BaseCommand
from shops.models import ServiceCategory, PredefinedService


class Command(BaseCommand):
    help = 'Populate the database with predefined barber services'

    def handle(self, *args, **options):
        # Create service categories
        categories_data = [
            {
                'name': 'haircut_men',
                'display_name': "Men's Haircuts",
                'description': 'Professional haircuts and styling for men'
            },
            {
                'name': 'haircut_women',
                'display_name': "Women's Haircuts",
                'description': 'Professional haircuts and styling for women'
            },
            {
                'name': 'beard',
                'display_name': 'Beard Styles',
                'description': 'Beard grooming and styling services'
            },
            {
                'name': 'spa_salon',
                'display_name': 'Spa & Salon Services',
                'description': 'Relaxing and beautifying spa treatments'
            }
        ]

        self.stdout.write("Creating service categories...")
        for cat_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"  ✓ Created category: {category.display_name}")
            else:
                self.stdout.write(f"  - Category exists: {category.display_name}")

        # Men's Haircut Services
        mens_haircuts = [
            ('Classic Fade', 'Traditional fade cut with scissor trim on top', 45),
            ('Taper Cut', 'Gradual length reduction with natural blend', 30),
            ('Crew Cut', 'Short military-style cut with uniform length', 25),
            ('Undercut', 'Short sides with longer top section', 40),
            ('Buzz Cut', 'Ultra-short all-over cut with clippers', 15),
            ('Pompadour', 'Vintage-style with volume on top, short sides', 50),
            ('Quiff', 'Modern style with textured top and faded sides', 45),
            ('Side Part', 'Classic professional look with defined part', 35),
            ('Textured Crop', 'Modern short cut with textured styling', 40),
            ('Slicked Back', 'Formal style with hair combed backwards', 30),
        ]

        # Women's Haircut Services
        womens_haircuts = [
            ('Bob Cut', 'Classic chin-length bob with clean lines', 60),
            ('Pixie Cut', 'Short, edgy cut that frames the face', 55),
            ('Layered Cut', 'Multi-layered cut for volume and movement', 70),
            ('Long Layers', 'Subtle layers for long hair with natural flow', 65),
            ('Shag Cut', 'Textured layers with a rock-and-roll vibe', 75),
            ('Lob (Long Bob)', 'Longer version of classic bob, shoulder-length', 65),
            ('Asymmetrical Cut', 'Edgy uneven lengths for modern look', 70),
            ('Bangs Trim', 'Fringe cutting and styling service', 20),
            ('Face-Framing Layers', 'Strategic layers to highlight facial features', 60),
            ('Blunt Cut', 'Straight across cut with no layers', 50),
        ]

        # Beard Services
        beard_services = [
            ('Classic Beard Trim', 'Professional beard shaping and trimming', 25),
            ('Goatee Styling', 'Precise goatee shaping and maintenance', 20),
            ('Full Beard Sculpt', 'Complete beard redesign and styling', 35),
            ('Stubble Shaping', 'Maintaining the perfect stubble length', 15),
            ('Mustache Trim', 'Precision mustache grooming', 10),
            ('Beard Line-up', 'Clean beard edges and neckline definition', 15),
            ('Hot Towel Shave', 'Traditional hot towel and straight razor shave', 45),
            ('Beard Oil Treatment', 'Conditioning treatment for beard health', 20),
        ]

        # Spa & Salon Services
        spa_salon_services = [
            ('Head Massage', 'Relaxing scalp and head massage', 30),
            ('Hair Spa Treatment', 'Deep conditioning and nourishing hair treatment', 90),
            ('Manicure', 'Complete nail care and polish application', 45),
            ('Pedicure', 'Foot care and nail treatment', 60),
            ('Facial Treatment', 'Deep cleansing and moisturizing facial', 75),
            ('Eyebrow Threading', 'Precision eyebrow shaping using threading', 15),
            ('Upper Lip Threading', 'Hair removal using threading technique', 10),
            ('Hair Coloring', 'Professional hair color application', 120),
            ('Highlights', 'Hair highlighting and color enhancement', 150),
            ('Blow Dry & Style', 'Professional hair drying and styling', 25),
            ('Hair Straightening', 'Chemical straightening treatment', 180),
            ('Keratin Treatment', 'Protein treatment for smooth, frizz-free hair', 200),
            ('Hot Oil Treatment', 'Deep conditioning hot oil hair treatment', 45),
            ('Scalp Treatment', 'Specialized scalp care and therapy', 60),
        ]

        # Create services for each category
        services_data = [
            ('haircut_men', mens_haircuts),
            ('haircut_women', womens_haircuts),
            ('beard', beard_services),
            ('spa_salon', spa_salon_services),
        ]

        self.stdout.write("\nCreating predefined services...")
        total_created = 0
        
        for category_name, services in services_data:
            try:
                category = ServiceCategory.objects.get(name=category_name)
                self.stdout.write(f"\nAdding services for {category.display_name}:")
                
                for service_name, description, duration in services:
                    service, created = PredefinedService.objects.get_or_create(
                        category=category,
                        name=service_name,
                        defaults={
                            'description': description,
                            'estimated_duration': duration,
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f"  ✓ {service_name} ({duration} min)")
                        total_created += 1
                    else:
                        self.stdout.write(f"  - {service_name} (exists)")
                        
            except ServiceCategory.DoesNotExist:
                self.stdout.write(f"Category {category_name} not found!")

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully populated {total_created} new services!'))
        self.stdout.write("You can now run migrations and start assigning services to shops.")