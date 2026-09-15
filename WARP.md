# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a comprehensive barber management system built with Django (backend) and Flask (real-time API services). The system enables barber shop owners to manage their operations and allows customers to find and book appointments with nearby barbers.

**Key Technologies:**
- **Backend**: Django 5.2.6 with custom User model and role-based authentication
- **Real-time API**: Flask 3.1.2 with Socket.IO for WebSocket connections
- **Database**: SQLite (development) with easy PostgreSQL/MySQL migration path
- **Frontend**: Django Templates with Bootstrap 5.3.0 and AOS animations
- **Location Services**: Geopy for geocoding and distance calculations
- **Image Processing**: Pillow for portfolio and AI photo uploads

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows PowerShell)
.\barber_env\Scripts\Activate.ps1

# Activate virtual environment (Windows CMD)
barber_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Django Development
```bash
# Navigate to Django backend
cd django_backend

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Populate initial data
python manage.py populate_services
python manage.py populate_haircut_data

# Create superuser
python manage.py createsuperuser

# Run Django development server (port 8000)
python manage.py runserver

# Run Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Run specific app tests
python manage.py test users
python manage.py test shops
python manage.py test appointments
```

### Flask API Service
```bash
# Navigate to Flask API directory
cd flask_api

# Run Flask development server (port 5000)
python app.py
```

### Database Operations
```bash
# Create new migration
python manage.py makemigrations <app_name>

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Reset database (development only)
# Delete db.sqlite3 and rerun migrations
```

## High-Level Architecture

### Multi-Service Architecture
The system uses a **hybrid architecture** with Django handling the main application logic and Flask providing real-time services:

1. **Django Backend** (`django_backend/`): Main application server handling authentication, business logic, and data persistence
2. **Flask API** (`flask_api/`): Microservice for real-time features including WebSocket connections, location services, and live waiting list updates
3. **Shared Database**: Both services connect to the same SQLite database for data consistency

### Core Django Applications

#### 1. Users App (`users/`)
- **Custom User Model**: Extends AbstractUser with role-based authentication (`customer` vs `shop_owner`)
- **Key Features**: Account deletion with GDPR compliance, location tracking, profile management
- **Models**: `User` with cascade deletion methods

#### 2. Shops App (`shops/`)
- **Core Models**: 
  - `Shop`: Main shop entity with location, operating hours, waiting list management
  - `ServiceCategory`: Hierarchical service organization (Men's/Women's Haircuts, Beard, Spa)
  - `PredefinedService`: 42 predefined services with descriptions and durations
  - `ShopService`: Shop-specific pricing and availability for services
  - `ShopPortfolioImage`: Portfolio gallery system with service categorization
  - `ShopReview`: 5-star rating system with one-review-per-customer policy
- **Business Logic**: Waiting list management, service pricing, portfolio management

#### 3. Appointments App (`appointments/`)
- **Multi-Service Bookings**: Single appointment can include multiple services
- **Models**: `Appointment` with ManyToMany relationship to `ShopService`
- **Features**: Special requests, automatic price/duration calculation, status tracking

#### 4. Waiting Lists App (`waiting_lists/`)
- **Real-time Updates**: Integration with Flask Socket.IO for live position updates
- **Queue Management**: Position tracking, estimated wait times

#### 5. Haircut Suggestions App (`haircut_suggestions/`)
- **AI-Powered Recommendations**: Face shape detection and haircut matching
- **Models**: `FaceShape`, `HaircutStyle`, `CustomerHaircutPhoto`, `HaircutSuggestion`
- **Features**: Photo upload, style browsing, compatibility scoring

### Data Flow Patterns

#### Authentication & Authorization
- Django's built-in authentication with custom User model
- Role-based access control (`@login_required`, role checks in views)
- Session-based authentication shared between Django and Flask

#### Real-time Communication
- Flask Socket.IO handles WebSocket connections for live updates
- Room-based messaging for shop-specific updates
- RESTful API endpoints in Flask for location services

#### Image Handling
- Secure upload paths for portfolio and customer photos
- Automatic file cleanup on deletion
- Size and type validation (5MB limit, specific formats)

### Database Design Philosophy

The system uses a **normalized relational design** with clear separation of concerns:
- User management separated from business entities
- Service definitions separated from shop-specific pricing
- Portfolio images linked to service categories for organization
- One-to-many and many-to-many relationships for flexibility

## Testing Framework

The project uses **Django's built-in testing framework**:
- Each app contains `tests.py` files
- Run tests with: `python manage.py test`
- Test individual apps: `python manage.py test <app_name>`

## Key Development Patterns

### Model Patterns
- **Custom User Model**: Always reference via `get_user_model()`
- **Cascade Deletion**: Comprehensive cleanup methods in User model for GDPR compliance
- **Calculated Properties**: Use `@property` for derived fields (e.g., `get_average_rating()`)
- **Manager Methods**: Business logic in model methods (e.g., `increase_waiting_count()`)

### View Patterns
- **Role-based Decorators**: Check user roles in views
- **Query Optimization**: Use `select_related()`/`prefetch_related()` for foreign keys
- **Form Handling**: Django forms for data validation and processing

### Template Patterns
- **Responsive Design**: Bootstrap 5.3.0 with mobile-first approach
- **Component Reuse**: Shared templates in `templates/` directory
- **AOS Animations**: Scroll animations for enhanced UX

### API Patterns (Flask)
- **CORS Configuration**: Specific origins for Django integration
- **Database Connections**: Direct SQLite connections with proper cleanup
- **Error Handling**: Consistent JSON error responses
- **WebSocket Rooms**: Room-based real-time updates

## Data Management

### Initial Data Setup
```bash
# Populate service categories and 42 predefined services
python manage.py populate_services

# Create face shapes and haircut styles for AI feature
python manage.py populate_haircut_data
```

### Management Commands Available
- `populate_services`: Creates service categories and 42 predefined services
- `populate_haircut_data`: Sets up face shapes and haircut styles for AI recommendations

### Key URLs and Endpoints

#### Django URLs
- Admin: `/admin/`
- User Dashboard: `/users/dashboard/`
- Shop Management: `/shops/dashboard/`
- Service Management: `/shops/manage/services/`
- Portfolio Management: `/shops/manage/portfolio/`
- Haircut AI: `/haircut-suggestions/`
- Account Deletion: `/users/delete-account/`

#### Flask API Endpoints
- Geocoding: `POST /api/location/geocode`
- Nearby Shops: `POST /api/shops/nearby`
- Real-time Waiting List: `GET /api/waiting-list/realtime/<shop_id>`
- Shop Search: `POST /api/search/shops`
- Health Check: `GET /api/health`

## Security Considerations

### File Upload Security
- Image upload validation (size, type, secure paths)
- Automatic cleanup on deletion
- Secure storage in `media/` directory

### Data Privacy (GDPR Compliant)
- Complete account deletion with `delete_account_data()` method
- Password verification required for account deletion
- Comprehensive data cleanup including files

### Authentication
- Role-based access control
- Session-based authentication
- CORS configuration for cross-service communication

## Production Deployment Notes

### Environment Variables
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS`
- Set secure `SECRET_KEY`
- Configure production database (PostgreSQL recommended)

### Static Files
- Run `python manage.py collectstatic`
- Configure web server for static file serving

### Database Migration Path
- Easy migration from SQLite to PostgreSQL/MySQL
- Update `DATABASES` setting in `settings.py`

## Common Troubleshooting

### Migration Issues
- Check for circular dependencies between apps
- Use `python manage.py showmigrations` to diagnose
- Reset development database if needed

### Flask Connection Issues
- Ensure Django server is running first (port 8000)
- Check Flask CORS configuration
- Verify database path in Flask app

### Image Upload Problems
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Verify directory permissions
- Ensure PIL/Pillow is installed correctly

### Real-time Features Not Working
- Confirm Flask Socket.IO server is running
- Check browser console for WebSocket connection errors
- Verify room joining/leaving logic in frontend JavaScript

This system represents a production-ready barber management platform with modern architecture patterns, comprehensive feature set, and scalable design principles.