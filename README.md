# Barber Management System

A comprehensive web-based barber management system built with Django (backend) and Flask (API services) that allows barber shop owners to manage their operations and customers to find and book appointments with nearby barbers.

## Features

### For Barber Shop Owners
- **Shop Registration**: Register and set up barber shop profiles
- **Waiting List Management**: Increase/decrease waiting list count with dedicated buttons
- **Client Management**: View customer details and manage appointments
- **Dashboard**: Real-time overview of shop operations
- **Appointment Management**: View and manage customer appointments

### For Customers
- **User Registration**: Sign up as a customer
- **Shop Discovery**: Find nearby barber shops with search functionality
- **Appointment Booking**: Book appointments at preferred shops
- **Waiting List**: Join waiting lists and track position in real-time
- **Location-based Search**: Find barbers near your location

### Technical Features
- **Modern UI/UX**: Clean black and white theme with minimal color accents
- **Real-time Updates**: WebSocket integration for live waiting list updates
- **Search Functionality**: Advanced search with location-based filtering
- **Responsive Design**: Mobile-friendly interface
- **RESTful APIs**: Flask microservice for real-time features
- **Role-based Authentication**: Separate functionality for customers and shop owners

## Technology Stack

- **Backend**: Django 5.2.6 (Python web framework)
- **API Services**: Flask 3.1.2 with Socket.IO for real-time features
- **Database**: SQLite (development) - easily configurable for PostgreSQL/MySQL
- **Frontend**: Django Templates with Bootstrap 5.3.0
- **Real-time**: Socket.IO for WebSocket connections
- **Location Services**: Geopy for geocoding and distance calculations
- **Icons**: Font Awesome 6.0.0
- **Authentication**: Django's built-in authentication with custom user roles

## Project Structure

```
barber-management-system/
├── django_backend/           # Main Django application
│   ├── barber_management/    # Django project settings
│   ├── users/               # User authentication and profiles
│   ├── shops/               # Barber shop management
│   ├── appointments/        # Appointment booking system
│   ├── waiting_lists/       # Waiting list management
│   └── templates/           # HTML templates
├── flask_api/               # Flask microservice for real-time features
│   └── app.py              # Flask application with Socket.IO
├── static/                  # Static files (CSS, JS, images)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

1. **Clone/Download the project** (you're already in the directory)

2. **Activate the virtual environment**:
   ```bash
   # Windows PowerShell
   .\\barber_env\\Scripts\\Activate.ps1
   
   # Windows Command Prompt
   barber_env\\Scripts\\activate
   
   # macOS/Linux
   source barber_env/bin/activate
   ```

3. **Install dependencies** (already done):
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Django migrations**:
   ```bash
   cd django_backend
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```
   The Django app will be available at `http://localhost:8000`

7. **Start the Flask API server** (in a new terminal):
   ```bash
   # Activate virtual environment first
   cd flask_api
   python app.py
   ```
   The Flask API will be available at `http://localhost:5000`

## Usage

### Getting Started

1. **Register as a Customer**:
   - Visit `http://localhost:8000/users/register/`
   - Select "Customer" as role
   - Fill in your details and register

2. **Register as a Shop Owner**:
   - Visit `http://localhost:8000/users/register/`
   - Select "Shop Owner" as role
   - After registration, set up your shop profile

3. **Shop Owner Features**:
   - Access shop dashboard to manage operations
   - Use increase/decrease buttons to manage waiting list
   - View customer details and appointments
   - Monitor real-time shop statistics

4. **Customer Features**:
   - Find nearby barber shops
   - Join waiting lists or book appointments
   - Track your position in waiting lists
   - Search for shops by name or location

### Key URLs

- **Home**: `http://localhost:8000/`
- **Login**: `http://localhost:8000/users/login/`
- **Register**: `http://localhost:8000/users/register/`
- **Customer Dashboard**: `http://localhost:8000/users/dashboard/`
- **Shop Owner Dashboard**: `http://localhost:8000/shops/dashboard/`
- **Find Shops**: `http://localhost:8000/shops/list/`
- **Admin Panel**: `http://localhost:8000/admin/`

## API Endpoints (Flask Service)

- **POST** `/api/location/geocode` - Convert address to coordinates
- **POST** `/api/shops/nearby` - Find nearby shops
- **GET** `/api/waiting-list/realtime/<shop_id>` - Real-time waiting list
- **POST** `/api/search/shops` - Search shops
- **GET** `/api/health` - Health check

## Real-time Features

The system includes WebSocket support for:
- Live waiting list updates
- Real-time shop status changes
- Instant notifications for customers and shop owners

## Contributing

This is a complete barber management system ready for development and deployment. You can extend it with additional features like:
- Payment integration
- SMS/Email notifications
- Advanced reporting and analytics
- Mobile application
- Multi-language support

## License

This project is created as a demonstration of a full-stack web application using Django and Flask.

## Support

For issues or questions about the system, please check the code documentation or create an issue in the project repository.