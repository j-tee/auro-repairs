# Frontend Developer API Documentation
## Auto Repair Shop Management System

> **🎯 UPDATED**: This documentation now accurately reflects the actual API responses after verifying database schema and serializer implementations.

---

## Table of Contents
1. [API Authentication](#api-authentication)
2. [Employee Management APIs](#employee-management-apis)
3. [Technician Workload APIs](#technician-workload-apis)
4. [Appointment Management APIs](#appointment-management-apis)
5. [Vehicle & Customer APIs](#vehicle--customer-apis)
6. [TypeScript Interfaces](#typescript-interfaces)
7. [Frontend Implementation Examples](#frontend-implementation-examples)
8. [Redux Integration Patterns](#redux-integration-patterns)
9. [Error Handling](#error-handling)

---

## API Authentication

All API endpoints require authentication. The system uses JWT tokens.

### Authentication Endpoints
```typescript
// Login
POST /api/auth/login/
{
  "username": "user@example.com",
  "password": "password123"
}

// Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "role": "owner"
  }
}
```

### Setting up Axios with Authentication
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Employee Management APIs

### 1. Get All Employees
```typescript
GET /api/shop/employees/
```

**✅ VERIFIED Response** (includes computed properties):
```json
[
  {
    "id": 27,
    "name": "Test Technician",
    "role": "technician",
    "phone_number": "555-0123",
    "email": "tech@test.com",
    "picture": null,
    "shop": 18,
    "user": null,
    "workload_count": 1,
    "is_available": true,
    "appointments_today_count": 0,
    "is_technician": true,
    "current_jobs": [
      {
        "appointment_id": 34,
        "vehicle": "Toyota Camry",
        "customer": "Alice Cooper",
        "status": "assigned",
        "date": "2025-08-22T10:30:00Z",
        "assigned_at": "2025-09-13T10:17:49.359466Z",
        "started_at": null
      }
    ]
  }
]
```

### 2. Get Individual Employee
```typescript
GET /api/shop/employees/{id}/
```

**Response**: Same structure as above, single employee object.

### 3. Frontend Implementation
```typescript
// Get all employees with workload data
const fetchEmployees = async (): Promise<Employee[]> => {
  const response = await api.get('/api/shop/employees/');
  return response.data;
};

// Get available technicians
const getAvailableTechnicians = async (): Promise<Employee[]> => {
  const employees = await fetchEmployees();
  return employees.filter(emp => emp.is_technician && emp.is_available);
};

// Get technician workload
const getTechnicianWorkload = (technician: Employee) => ({
  currentJobs: technician.current_jobs.length,
  isAvailable: technician.is_available,
  todayAppointments: technician.appointments_today_count
});
```

---

## Technician Workload APIs

### 1. Specialized Workload Endpoint
```typescript
GET /api/shop/technicians/workload/
```

**Response**:
```json
{
  "summary": {
    "total_technicians": 3,
    "available_technicians": 2,
    "busy_technicians": 1
  },
  "technicians": [
    {
      "technician": {
        "id": 27,
        "name": "Test Technician",
        "role": "technician",
        "shop": "Main Shop"
      },
      "workload": {
        "current_appointments": 1,
        "is_available": true,
        "appointments_today": 0,
        "max_capacity": 3
      },
      "current_jobs": [
        {
          "appointment_id": 34,
          "vehicle": "Toyota Camry",
          "customer": "Alice Cooper",
          "status": "assigned",
          "assigned_at": "2025-09-13T10:17:49.359466Z",
          "started_at": null
        }
      ]
    }
  ]
}
```

### 2. Frontend Implementation
```typescript
// Get workload dashboard data
const fetchWorkloadDashboard = async () => {
  const response = await api.get('/api/shop/technicians/workload/');
  return response.data;
};

// Find least busy technician
const findBestTechnician = (workloadData: WorkloadResponse) => {
  return workloadData.technicians
    .filter(t => t.workload.is_available)
    .sort((a, b) => a.workload.current_appointments - b.workload.current_appointments)[0];
};
```

---

## Appointment Management APIs

### 1. Get All Appointments
```typescript
GET /api/shop/appointments/
```

**✅ VERIFIED Response**:
```json
[
  {
    "id": 34,
    "vehicle_id": 12,
    "vehicle": {
      "id": 12,
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "license_plate": "ABC-5189",
      "vin": "1HGBH41JXMN109186",
      "color": "Blue"
    },
    "reported_problem_id": null,
    "reported_problem": null,
    "assigned_technician_id": 27,
    "assigned_technician": {
      "id": 27,
      "name": "Test Technician",
      "role": "technician"
    },
    "customer_id": 15,
    "customer_name": "Alice Cooper",
    "description": "Engine noise inspection",
    "date": "2025-08-22T10:30:00Z",
    "status": "assigned",
    "assigned_at": "2025-09-13T10:17:49.359466Z",
    "started_at": null,
    "completed_at": null
  }
]
```

### 2. Technician Assignment Actions
```typescript
// Assign technician to appointment
POST /api/shop/appointments/{id}/assign-technician/
{
  "technician_id": 27
}

// Start work on appointment
POST /api/shop/appointments/{id}/start-work/

// Complete work on appointment  
POST /api/shop/appointments/{id}/complete-work/
```

**Response**: Updated appointment object with new status and timestamps.

### 3. Frontend Implementation
```typescript
// Assign technician
const assignTechnician = async (appointmentId: number, technicianId: number) => {
  const response = await api.post(
    `/api/shop/appointments/${appointmentId}/assign-technician/`,
    { technician_id: technicianId }
  );
  return response.data;
};

// Update appointment status
const startWork = async (appointmentId: number) => {
  const response = await api.post(`/api/shop/appointments/${appointmentId}/start-work/`);
  return response.data;
};

const completeWork = async (appointmentId: number) => {
  const response = await api.post(`/api/shop/appointments/${appointmentId}/complete-work/`);
  return response.data;
};
```

---

## Vehicle & Customer APIs

### 1. Vehicles
```typescript
GET /api/shop/vehicles/

// Response includes customer data
{
  "id": 12,
  "make": "Toyota", 
  "model": "Camry",
  "year": 2020,
  "license_plate": "ABC-5189",
  "vin": "1HGBH41JXMN109186",
  "color": "Blue",
  "customer_id": 15,
  "customer": {
    "id": 15,
    "name": "Alice Cooper",
    "email": "alice@example.com",
    "phone_number": "555-0199"
  },
  "customer_name": "Alice Cooper",
  "customer_email": "alice@example.com",
  "customer_phone": "555-0199"
}
```

### 2. Customers
```typescript
GET /api/shop/customers/

{
  "id": 15,
  "name": "Alice Cooper",
  "phone_number": "555-0199", 
  "email": "alice@example.com",
  "address": "123 Main St",
  "user": null
}
```

---

## TypeScript Interfaces

```typescript
// Employee interfaces
interface Employee {
  id: number;
  name: string;
  role: string;
  phone_number: string;
  email: string | null;
  picture: string | null;
  shop: number;
  user: number | null;
  // Computed properties
  workload_count: number;
  is_available: boolean;
  appointments_today_count: number;
  is_technician: boolean;
  current_jobs: CurrentJob[];
}

interface CurrentJob {
  appointment_id: number;
  vehicle: string;
  customer: string;
  status: string;
  date: string;
  assigned_at: string;
  started_at: string | null;
}

// Appointment interfaces  
interface Appointment {
  id: number;
  vehicle_id: number;
  vehicle: Vehicle;
  reported_problem_id: number | null;
  reported_problem: VehicleProblem | null;
  assigned_technician_id: number | null;
  assigned_technician: TechnicianSummary | null;
  customer_id: number;
  customer_name: string;
  description: string;
  date: string;
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  assigned_at: string | null;
  started_at: string | null;
  completed_at: string | null;
}

interface TechnicianSummary {
  id: number;
  name: string;
  role: string;
}

interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  license_plate: string;
  vin: string;
  color: string;
}

interface Customer {
  id: number;
  name: string;
  phone_number: string;
  email: string | null;
  address: string | null;
  user: number | null;
}

// Workload interfaces
interface WorkloadResponse {
  summary: {
    total_technicians: number;
    available_technicians: number;
    busy_technicians: number;
  };
  technicians: TechnicianWorkload[];
}

interface TechnicianWorkload {
  technician: {
    id: number;
    name: string;
    role: string;
    shop: string;
  };
  workload: {
    current_appointments: number;
    is_available: boolean;
    appointments_today: number;
    max_capacity: number;
  };
  current_jobs: CurrentJob[];
}
```

---

## Frontend Implementation Examples

### 1. React Hook for Employee Management
```tsx
import { useState, useEffect } from 'react';

export const useEmployees = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/shop/employees/');
      setEmployees(response.data);
    } catch (err) {
      setError('Failed to fetch employees');
    } finally {
      setLoading(false);
    }
  };

  const getAvailableTechnicians = () => 
    employees.filter(emp => emp.is_technician && emp.is_available);

  const getTechnicianById = (id: number) => 
    employees.find(emp => emp.id === id && emp.is_technician);

  return {
    employees,
    loading,
    error,
    getAvailableTechnicians,
    getTechnicianById,
    refetch: fetchEmployees
  };
};
```

### 2. Appointment Management Component
```tsx
import React from 'react';
import { useEmployees } from './hooks/useEmployees';

interface AppointmentCardProps {
  appointment: Appointment;
  onStatusChange: (appointmentId: number) => void;
}

const AppointmentCard: React.FC<AppointmentCardProps> = ({ 
  appointment, 
  onStatusChange 
}) => {
  const { getAvailableTechnicians } = useEmployees();
  const availableTechnicians = getAvailableTechnicians();

  const handleAssignTechnician = async (technicianId: number) => {
    try {
      await assignTechnician(appointment.id, technicianId);
      onStatusChange(appointment.id);
    } catch (error) {
      console.error('Failed to assign technician:', error);
    }
  };

  const handleStartWork = async () => {
    try {
      await startWork(appointment.id);
      onStatusChange(appointment.id);
    } catch (error) {
      console.error('Failed to start work:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-blue-100 text-blue-800';
      case 'assigned': return 'bg-yellow-100 text-yellow-800';
      case 'in_progress': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="border rounded-lg p-4 shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold">
            {appointment.vehicle.make} {appointment.vehicle.model}
          </h3>
          <p className="text-gray-600">{appointment.customer_name}</p>
        </div>
        <span className={`px-2 py-1 rounded text-sm ${getStatusColor(appointment.status)}`}>
          {appointment.status}
        </span>
      </div>

      <p className="text-gray-700 mb-3">{appointment.description}</p>

      {appointment.assigned_technician && (
        <div className="mb-3 p-2 bg-gray-50 rounded">
          <p className="text-sm">
            <strong>Assigned to:</strong> {appointment.assigned_technician.name}
          </p>
          {appointment.assigned_at && (
            <p className="text-xs text-gray-500">
              Assigned: {new Date(appointment.assigned_at).toLocaleString()}
            </p>
          )}
        </div>
      )}

      <div className="flex gap-2 mt-3">
        {appointment.status === 'pending' && (
          <select 
            onChange={(e) => handleAssignTechnician(Number(e.target.value))}
            defaultValue=""
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="" disabled>Assign Technician</option>
            {availableTechnicians.map(tech => (
              <option key={tech.id} value={tech.id}>
                {tech.name} (Load: {tech.workload_count}/3)
              </option>
            ))}
          </select>
        )}

        {appointment.status === 'assigned' && (
          <button
            onClick={handleStartWork}
            className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
          >
            Start Work
          </button>
        )}

        {appointment.status === 'in_progress' && (
          <button
            onClick={() => completeWork(appointment.id)}
            className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
          >
            Complete Work
          </button>
        )}
      </div>
    </div>
  );
};
```

### 3. Workload Dashboard Component
```tsx
const WorkloadDashboard: React.FC = () => {
  const [workloadData, setWorkloadData] = useState<WorkloadResponse | null>(null);

  useEffect(() => {
    fetchWorkloadData();
    const interval = setInterval(fetchWorkloadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchWorkloadData = async () => {
    try {
      const data = await fetchWorkloadDashboard();
      setWorkloadData(data);
    } catch (error) {
      console.error('Failed to fetch workload data:', error);
    }
  };

  if (!workloadData) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Summary Cards */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">Available Technicians</h3>
        <p className="text-3xl font-bold text-green-600">
          {workloadData.summary.available_technicians}
        </p>
        <p className="text-gray-500">
          out of {workloadData.summary.total_technicians}
        </p>
      </div>

      {/* Technician List */}
      <div className="md:col-span-2">
        <h3 className="text-lg font-semibold mb-4">Technician Status</h3>
        <div className="space-y-3">
          {workloadData.technicians.map(tech => (
            <div key={tech.technician.id} className="border rounded p-3">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium">{tech.technician.name}</h4>
                <span className={`px-2 py-1 rounded text-sm ${
                  tech.workload.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {tech.workload.is_available ? 'Available' : 'Busy'}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <p>Current jobs: {tech.workload.current_appointments}/{tech.workload.max_capacity}</p>
                <p>Today's appointments: {tech.workload.appointments_today}</p>
              </div>
              {tech.current_jobs.length > 0 && (
                <div className="mt-2 text-xs">
                  <p className="font-medium">Current Jobs:</p>
                  {tech.current_jobs.map(job => (
                    <p key={job.appointment_id} className="text-gray-500">
                      • {job.vehicle} - {job.customer} ({job.status})
                    </p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

---

## Redux Integration Patterns

### 1. Store Structure
```typescript
interface AppState {
  employees: {
    items: Employee[];
    loading: boolean;
    error: string | null;
  };
  appointments: {
    items: Appointment[];
    loading: boolean;
    error: string | null;
  };
  workload: {
    data: WorkloadResponse | null;
    loading: boolean;
    lastUpdated: string | null;
  };
}
```

### 2. Redux Slice (using Redux Toolkit)
```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks
export const fetchEmployees = createAsyncThunk(
  'employees/fetchEmployees',
  async () => {
    const response = await api.get('/api/shop/employees/');
    return response.data;
  }
);

export const assignTechnicianThunk = createAsyncThunk(
  'appointments/assignTechnician',
  async ({ appointmentId, technicianId }: { appointmentId: number, technicianId: number }) => {
    const response = await api.post(
      `/api/shop/appointments/${appointmentId}/assign-technician/`,
      { technician_id: technicianId }
    );
    return response.data;
  }
);

// Slice
const employeesSlice = createSlice({
  name: 'employees',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchEmployees.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEmployees.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchEmployees.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch employees';
      });
  },
});

// Selectors
export const selectAvailableTechnicians = (state: AppState) =>
  state.employees.items.filter(emp => emp.is_technician && emp.is_available);

export const selectTechnicianWorkload = (state: AppState, technicianId: number) => {
  const technician = state.employees.items.find(emp => emp.id === technicianId);
  return technician ? {
    workload: technician.workload_count,
    available: technician.is_available,
    currentJobs: technician.current_jobs
  } : null;
};
```

### 3. Using in Components
```tsx
import { useSelector, useDispatch } from 'react-redux';
import { fetchEmployees, assignTechnicianThunk } from './store/employeesSlice';

const AppointmentManager: React.FC = () => {
  const dispatch = useDispatch();
  const employees = useSelector((state: AppState) => state.employees.items);
  const availableTechnicians = useSelector(selectAvailableTechnicians);

  useEffect(() => {
    dispatch(fetchEmployees());
  }, [dispatch]);

  const handleAssignTechnician = (appointmentId: number, technicianId: number) => {
    dispatch(assignTechnicianThunk({ appointmentId, technicianId }));
  };

  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};
```

---

## Error Handling

### 1. API Error Types
```typescript
interface ApiError {
  message: string;
  status: number;
  details?: Record<string, string[]>;
}

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle authentication error
      localStorage.removeItem('accessToken');
      window.location.href = '/login';
    }
    
    const apiError: ApiError = {
      message: error.response?.data?.detail || error.message,
      status: error.response?.status || 0,
      details: error.response?.data
    };
    
    return Promise.reject(apiError);
  }
);
```

### 2. Error Handling Hook
```typescript
export const useErrorHandler = () => {
  const [error, setError] = useState<string | null>(null);

  const handleError = useCallback((error: ApiError) => {
    setError(error.message);
    // Log to error reporting service
    console.error('API Error:', error);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
};
```

---

## Summary

### ✅ Key Points for Frontend Developers

1. **Employee API** (`/api/shop/employees/`) now includes computed properties:
   - `workload_count`, `is_available`, `appointments_today_count`
   - `is_technician`, `current_jobs`

2. **Consistent Field Patterns**: All APIs provide both ID and object data:
   - `vehicle_id` + `vehicle` object
   - `assigned_technician_id` + `assigned_technician` object

3. **Real-time Workload**: Employee data includes live workload information without additional API calls

4. **Technician Assignment Workflow**:
   - `pending` → assign technician → `assigned` → start work → `in_progress` → complete → `completed`

5. **Authentication**: All endpoints require JWT Bearer token authentication

This documentation reflects the actual, verified API behavior and provides comprehensive examples for frontend implementation.