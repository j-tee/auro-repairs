# Customer Dashboard Backend API Documentation

## 📋 Overview

This documentation provides comprehensive information about the Customer Dashboard Backend API implementation for the Auto Repairs Management System. The backend provides secure, customer-specific endpoints for accessing appointments, vehicles, and repair orders.

## 🔐 Authentication

All customer dashboard endpoints require JWT authentication using Bearer tokens.

### Getting Authentication Token

**Endpoint:** `POST /api/token/`

```json
// Request
{
    "email": "customer@example.com",
    "password": "password123"
}

// Response
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using Authentication Token

Include the access token in the Authorization header for all API requests:

```javascript
headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
}
```

## 🏠 Customer Dashboard API Endpoints

### 1. Customer Profile Endpoint

Get authenticated customer's profile information.

**Endpoint:** `GET /api/auth/customer-profile/`

**Authentication:** Required (JWT Bearer Token)

**Response:**
```json
{
    "user_id": 71,
    "customer": {
        "id": 19,
        "name": "Alice Cooper",
        "email": "alice.cooper@customer.com",
        "phone": "(555) 714-5422",
        "address": "123 Elm St, Springfield, NY 10001"
    },
    "user_role": "customer"
}
```

**JavaScript Example:**
```javascript
const getCustomerProfile = async (token) => {
    const response = await fetch('/api/auth/customer-profile/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};
```

### 2. Customer Appointments Endpoint

Get all appointments for the authenticated customer.

**Endpoint:** `GET /api/shop/appointments/customers/me/appointments/`

**Authentication:** Required (JWT Bearer Token)

**Query Parameters:**
- `status` (optional): Filter by appointment status (comma-separated)
  - Values: `pending`, `in_progress`, `completed`, `cancelled`
  - Example: `?status=pending,in_progress`
- `dateFrom` (optional): Start date filter (YYYY-MM-DD format)
- `dateTo` (optional): End date filter (YYYY-MM-DD format)

**Response:**
```json
{
    "results": [
        {
            "id": 53,
            "vehicle_id": 40,
            "vehicle": {
                "id": 40,
                "make": "Honda",
                "model": "Civic",
                "year": 2020,
                "license_plate": "ABC-123",
                "vin": "1HGBH41JXMN109186",
                "color": "Silver"
            },
            "reported_problem_id": null,
            "reported_problem": null,
            "assigned_technician_id": null,
            "assigned_technician": {
                "id": 27,
                "name": "Test Technician",
                "role": "technician",
                "email": "tech@test.com",
                "user_id": null
            },
            "customer_id": 19,
            "customer_name": "Alice Cooper",
            "description": "Oil change and tire rotation",
            "date": "2025-09-17T10:00:00Z",
            "status": "pending",
            "assigned_at": null,
            "started_at": null,
            "completed_at": null
        }
    ],
    "count": 7,
    "customer_id": 19,
    "customer_name": "Alice Cooper"
}
```

**JavaScript Example:**
```javascript
// Get all appointments
const getCustomerAppointments = async (token) => {
    const response = await fetch('/api/shop/appointments/customers/me/appointments/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};

// Get filtered appointments
const getActiveAppointments = async (token) => {
    const response = await fetch('/api/shop/appointments/customers/me/appointments/?status=pending,in_progress', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};

// Get appointments by date range
const getAppointmentsByDateRange = async (token, fromDate, toDate) => {
    const url = `/api/shop/appointments/customers/me/appointments/?dateFrom=${fromDate}&dateTo=${toDate}`;
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};
```

### 3. Customer Vehicles Endpoint

Get all vehicles owned by the authenticated customer.

**Endpoint:** `GET /api/shop/vehicles/customers/me/vehicles/`

**Authentication:** Required (JWT Bearer Token)

**Response:**
```json
{
    "results": [
        {
            "id": 40,
            "customer": {
                "id": 19,
                "name": "Alice Cooper",
                "phone_number": "(555) 714-5422",
                "email": "alice.cooper@customer.com",
                "address": "123 Elm St, Springfield, NY 10001",
                "user": 71
            },
            "customer_name": "Alice Cooper",
            "make": "Honda",
            "model": "Civic",
            "year": 2020,
            "vin": "1HGBH41JXMN109186",
            "license_plate": "ABC-123",
            "color": "Silver",
            "customer_email": "alice.cooper@customer.com",
            "customer_phone": "(555) 714-5422"
        }
    ],
    "count": 3,
    "customer_id": 19,
    "customer_name": "Alice Cooper"
}
```

**JavaScript Example:**
```javascript
const getCustomerVehicles = async (token) => {
    const response = await fetch('/api/shop/vehicles/customers/me/vehicles/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};
```

### 4. Customer Repair Orders Endpoint

Get all repair orders for the authenticated customer's vehicles.

**Endpoint:** `GET /api/shop/repair-orders/customers/me/repair-orders/`

**Authentication:** Required (JWT Bearer Token)

**Query Parameters:**
- `status` (optional): Filter by repair order status (comma-separated)
  - Values: `pending`, `in_progress`, `completed`

**Response:**
```json
{
    "results": [
        {
            "id": 9,
            "vehicle_id": 27,
            "vehicle": {
                "id": 27,
                "make": "Toyota",
                "model": "Camry",
                "year": 2020,
                "license_plate": "ABC-5189",
                "vin": "1HGBH41JXMN118133",
                "color": "Silver"
            },
            "customer_id": 19,
            "customer_name": "Alice Cooper",
            "status": "in_progress",
            "discount_amount": "0.00",
            "discount_percent": "0.00",
            "tax_percent": "8.25",
            "total_cost": "363.67",
            "date_created": "2025-08-19T11:51:29.821036Z",
            "notes": "Repair work for Toyota Camry",
            "repair_order_parts": [
                {
                    "id": 21,
                    "part": {
                        "id": 136,
                        "name": "Transmission Fluid",
                        "part_number": "TRANS-FLUID-001-17",
                        "manufacturer": "Valvoline",
                        "unit_price": "18.99",
                        "taxable": true,
                        "warranty_months": 0
                    },
                    "quantity": 2,
                    "total_price": "37.98"
                }
            ],
            "repair_order_services": [
                {
                    "id": 18,
                    "service": {
                        "id": 134,
                        "name": "Tire Rotation",
                        "description": "Rotate and balance tires",
                        "labor_cost": "50.00",
                        "taxable": true,
                        "warranty_months": 6
                    }
                }
            ],
            "calculated_total_cost": "363.67"
        }
    ],
    "count": 16,
    "customer_id": 19,
    "customer_name": "Alice Cooper"
}
```

**JavaScript Example:**
```javascript
// Get all repair orders
const getCustomerRepairOrders = async (token) => {
    const response = await fetch('/api/shop/repair-orders/customers/me/repair-orders/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};

// Get active repair orders only
const getActiveRepairOrders = async (token) => {
    const response = await fetch('/api/shop/repair-orders/customers/me/repair-orders/?status=pending,in_progress', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
};
```

## 🔒 Security & Authorization

### Access Control
- All endpoints require JWT authentication
- Customers can **ONLY** access their own data
- Invalid or missing tokens return `401 Unauthorized`
- Non-customer users are rejected with `403 Forbidden`

### Error Responses

**401 Unauthorized (Invalid/Missing Token):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden (Wrong User Role):**
```json
{
    "error": "Access denied",
    "detail": "This endpoint is only accessible to customers."
}
```

**404 Not Found (No Customer Record):**
```json
{
    "error": "No customer record found for this user",
    "detail": "This user account is not linked to a customer record. Please contact support."
}
```

## 🧩 Frontend Integration Guide

### Complete Customer Dashboard Service

Here's a complete JavaScript service class for integrating with the Customer Dashboard API:

```javascript
class CustomerDashboardService {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('accessToken');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('accessToken', token);
    }

    getHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async handleResponse(response) {
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('accessToken');
                throw new Error('Authentication required');
            }
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        return response.json();
    }

    // Authentication
    async authenticate(email, password) {
        const response = await fetch(`${this.baseURL}/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await this.handleResponse(response);
        this.setToken(data.access);
        return data;
    }

    // Customer Profile
    async getCustomerProfile() {
        const response = await fetch(`${this.baseURL}/auth/customer-profile/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // Customer Appointments
    async getCustomerAppointments(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.dateFrom) params.append('dateFrom', filters.dateFrom);
        if (filters.dateTo) params.append('dateTo', filters.dateTo);

        const url = `${this.baseURL}/shop/appointments/customers/me/appointments/?${params}`;
        const response = await fetch(url, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // Customer Vehicles
    async getCustomerVehicles() {
        const response = await fetch(`${this.baseURL}/shop/vehicles/customers/me/vehicles/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // Customer Repair Orders
    async getCustomerRepairOrders(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);

        const url = `${this.baseURL}/shop/repair-orders/customers/me/repair-orders/?${params}`;
        const response = await fetch(url, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // Dashboard Summary (combines all data)
    async getDashboardSummary() {
        try {
            const [profile, appointments, vehicles, repairOrders] = await Promise.all([
                this.getCustomerProfile(),
                this.getCustomerAppointments(),
                this.getCustomerVehicles(),
                this.getCustomerRepairOrders()
            ]);

            return {
                profile,
                appointments,
                vehicles,
                repairOrders,
                summary: {
                    totalAppointments: appointments.count,
                    totalVehicles: vehicles.count,
                    totalRepairOrders: repairOrders.count,
                    activeAppointments: appointments.results.filter(
                        apt => ['pending', 'in_progress'].includes(apt.status)
                    ).length
                }
            };
        } catch (error) {
            console.error('Dashboard summary error:', error);
            throw error;
        }
    }
}

// Usage Example
const dashboardService = new CustomerDashboardService();

// Login and load dashboard
async function loadCustomerDashboard(email, password) {
    try {
        await dashboardService.authenticate(email, password);
        const dashboardData = await dashboardService.getDashboardSummary();
        
        console.log('Customer Dashboard Data:', dashboardData);
        return dashboardData;
    } catch (error) {
        console.error('Dashboard load error:', error);
        throw error;
    }
}
```

### React Hook Example

```javascript
import { useState, useEffect } from 'react';

export const useCustomerDashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const dashboardService = new CustomerDashboardService();

    const loadDashboard = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await dashboardService.getDashboardSummary();
            setDashboardData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            dashboardService.setToken(token);
            loadDashboard();
        } else {
            setLoading(false);
        }
    }, []);

    return {
        dashboardData,
        loading,
        error,
        refresh: loadDashboard
    };
};
```

## 📊 Data Structure Summary

### Key Data Models

**Customer Profile:**
- `user_id`: User account ID
- `customer.id`: Customer record ID  
- `customer.name`: Full name
- `customer.email`: Email address
- `customer.phone`: Phone number
- `customer.address`: Address

**Appointment:**
- `id`: Appointment ID
- `vehicle_id`: Associated vehicle ID
- `vehicle`: Complete vehicle object
- `assigned_technician`: Technician details (if assigned)
- `description`: Appointment description
- `date`: Appointment date/time (ISO format)
- `status`: `pending`, `in_progress`, `completed`, `cancelled`

**Vehicle:**
- `id`: Vehicle ID
- `make`, `model`, `year`: Vehicle details
- `vin`: Vehicle identification number
- `license_plate`: License plate
- `color`: Vehicle color

**Repair Order:**
- `id`: Repair order ID
- `vehicle_id`: Associated vehicle ID
- `status`: Current status
- `total_cost`: Total repair cost
- `repair_order_parts`: Array of parts used
- `repair_order_services`: Array of services performed
- `calculated_total_cost`: Computed total with tax/discounts

## 🚀 Testing

All endpoints have been thoroughly tested with:
- ✅ JWT authentication validation
- ✅ Customer data isolation (security)
- ✅ Query parameter filtering
- ✅ Error handling (401, 403, 404)
- ✅ Response format validation
- ✅ Performance with real data

### Test Customer Account
- **Email:** `alice.cooper@customer.com`
- **Password:** `password123`
- **Customer ID:** 19
- **Test Data:** 7 appointments, 3 vehicles, 16 repair orders

## 🔧 Technical Notes

### Backend Stack
- **Framework:** Django 5.2.5 with Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (Simple JWT)
- **Permissions:** Custom role-based permissions

### Performance Considerations
- All endpoints use optimized queries with `select_related` and `prefetch_related`
- Customer data is pre-filtered at the database level
- Responses include metadata (count, customer info) for efficient frontend handling

### Future Enhancements
- Pagination support for large datasets
- Real-time updates via WebSockets
- Notification system integration
- Mobile app API compatibility

## 📞 Support & Questions

For backend API questions or issues:
1. Check the error responses for specific details
2. Verify JWT token validity and format
3. Ensure customer role and account linking
4. Contact the backend development team with specific error messages

---

**Last Updated:** September 16, 2025  
**API Version:** 1.0  
**Backend Status:** Production Ready ✅