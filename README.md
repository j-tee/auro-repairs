# Auto Repairs Management System

A comprehensive Django-based backend system for managing auto repair shop operations, including customer management, vehicle tracking, repair orders, appointments, and technician allocation.

## Features

- **Customer Management**: Customer profiles, authentication, and dashboard access
- **Vehicle Management**: Vehicle tracking and customer associations
- **Repair Orders**: Complete repair order lifecycle management
- **Appointment System**: Scheduling and technician assignment
- **Authentication**: JWT-based authentication with role-based access control
- **API**: RESTful API endpoints for frontend integration

## Quick Start

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `auto_repairs_backend/` - Main Django application with authentication
- `shop/` - Shop management models, views, and API endpoints
- `manage.py` - Django management script

## API Documentation

The system provides RESTful API endpoints for:

- Customer authentication and profiles
- Customer-specific appointments, vehicles, and repair orders
- Shop management operations
- JWT token-based authentication

## Environment Configuration

- `.env.development` - Development environment settings
- `.env.production` - Production environment settings

## Status

✅ **Production Ready** - Backend implementation complete with comprehensive API endpoints, authentication, and security features.