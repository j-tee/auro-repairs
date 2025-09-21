# 🎯 TECHNICIAN ASSIGNMENT SYSTEM
## Frontend Developer Integration Guide

### 📋 Overview
This document outlines the **Technician Assignment System** implementation for appointment workflow management. This is a new feature that allows appointments to be assigned to technicians with complete workflow tracking.

---

## 🔧 SYSTEM OVERVIEW

> **🔧 IMPORTANT ENTITY CLARIFICATION**: **Technicians are Employees** - there's no separate technician entity. A technician is simply an employee with a role like "technician" or "mechanic". Use `employee_id` when referencing technicians in forms and APIs.

### Appointment Workflow
```javascript
// APPOINTMENT WORKFLOW STATUSES
const APPOINTMENT_STATUSES = {
  PENDING: 'pending',        // Customer booked appointment (initial status)
  ASSIGNED: 'assigned',      // Technician assigned but not started
  IN_PROGRESS: 'in_progress', // Work has begun
  COMPLETED: 'completed',    // Work finished
  CANCELLED: 'cancelled'     // Appointment cancelled
};

// Workflow transitions:
// pending → assigned → in_progress → completed
```

### New Appointment Fields
```javascript
// NEW APPOINTMENT RESPONSE STRUCTURE
const appointmentResponse = {
  id: 27,
  vehicle_id: 27,
  vehicle: { /* vehicle object */ },
  customer_id: 19,
  customer_name: "Alice Cooper",
  
  // 🎯 NEW TECHNICIAN FIELDS (technician is an Employee)
  assigned_technician_id: 5,        // Employee ID (same as employee_id)
  assigned_technician: {            // Employee object for display
    id: 5,
    name: "John Smith",
    role: "technician"              // Employee with technician role
  },
  
  // 🎯 NEW TIMESTAMP FIELDS
  assigned_at: "2025-09-13T09:44:37Z",  // When technician assigned
  started_at: "2025-09-13T10:15:22Z",   // When work began
  completed_at: null,                    // When work finished
  
  status: "in_progress",
  date: "2025-09-13T08:00:00Z",
  description: "Engine noise inspection"
};
```

---

## 📚 NEW API ENDPOINTS

### Axios Configuration (Recommended Setup)
```javascript
// api.js - Axios configuration with interceptors
import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 1. Technician Assignment
```javascript
// Note: All examples use configured axios instance (see above)
import api from './api';

// Assign technician (employee) to appointment
const assignTechnician = async (appointmentId, employeeId) => {
  const response = await api.post(`/api/shop/appointments/${appointmentId}/assign-technician/`, {
    technician_id: employeeId  // Employee ID (technician is an employee)
  });
  
  return response.data;
  // Returns: appointment data + assignment details
};
```

### 2. Work Progress Tracking
```javascript
// Start work (assigned → in_progress)
const startWork = async (appointmentId) => {
  const response = await api.post(`/api/shop/appointments/${appointmentId}/start-work/`);
  return response.data;
};

// Complete work (in_progress → completed)
const completeWork = async (appointmentId) => {
  const response = await api.post(`/api/shop/appointments/${appointmentId}/complete-work/`);
  return response.data;
};
```

### 3. Technician Workload Management
```javascript
// Get all technician workloads
const getTechnicianWorkload = async () => {
  const response = await api.get('/api/shop/technicians/workload/');
  return response.data;
  /*
  Returns:
  {
    "summary": {
      "total_technicians": 3,
      "available_technicians": 2,
      "busy_technicians": 1,
      "utilization_rate": "33.3%"
    },
    "technicians": [
      {
        "technician": {
          "id": 5,
          "name": "John Smith",
          "role": "technician"
        },
        "workload": {
          "current_appointments": 2,
          "is_available": true,
          "max_capacity": 3
        },
        "current_jobs": [...]
      }
    ]
  }
  */
};

// Get only available technicians (employees with technician role)
const getAvailableTechnicians = async () => {
  const response = await api.get('/api/shop/technicians/available/');
  return response.data;
  // Returns: Array of Employee objects where role contains "technician"
};
```

---

## 🎨 FRONTEND IMPLEMENTATION EXAMPLES

> **🚨 IMPLEMENTATION DISCLAIMER**: All code examples below are **samples for reference only**. Since your frontend uses Redux and has its own architecture, please:
> 
> - ✅ **Adapt patterns** to your existing Redux store structure
> - ✅ **Integrate with your component patterns** and styling system  
> - ✅ **Follow your team's coding standards** and conventions
> - ❌ **Do NOT copy and paste directly** - use these as implementation guides
> - ❌ **Do NOT replace your existing state management** - adapt these patterns

### 1. TypeScript Interfaces

```typescript
// Note: All API calls use axios - install with: npm install axios
// import axios from 'axios';

interface Employee {
  id: number;
  name: string;
  role: string;          // e.g., "technician", "mechanic", "receptionist"
  phone_number: string;
  email: string;
  // Note: Technicians are employees with role containing "technician" or "mechanic"
}

interface Appointment {
  id: number;
  vehicle_id: number;
  vehicle: Vehicle;
  customer_id: number;
  customer_name: string;
  
  // 🎯 NEW TECHNICIAN FIELDS (technician is an Employee)
  assigned_technician_id: number | null;  // Employee ID
  assigned_technician: Employee | null;   // Employee object
  
  // 🎯 NEW TIMESTAMP FIELDS
  assigned_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  date: string;
  description: string;
}

interface TechnicianWorkload {
  technician: Employee;    // Employee with technician role
  workload: {
    current_appointments: number;
    is_available: boolean;
    appointments_today: number;
    max_capacity: number;
  };
  current_jobs: Array<{
    appointment_id: number;
    vehicle: string;
    customer: string;
    status: string;
    assigned_at: string;
    started_at: string | null;
  }>;
}
```

### 2. Redux Integration Patterns

```javascript
// SAMPLE: How to integrate with Redux

// 1. Actions (Redux Toolkit)
const appointmentSlice = createSlice({
  name: 'appointments',
  initialState: {
    appointments: [],
    technicians: [],
    loading: false,
  },
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setAppointments: (state, action) => {
      state.appointments = action.payload;
    },
    updateAppointment: (state, action) => {
      const index = state.appointments.findIndex(apt => apt.id === action.payload.id);
      if (index >= 0) {
        state.appointments[index] = action.payload;
      }
    },
    setTechnicians: (state, action) => {
      state.technicians = action.payload;
    },
  },
});

// 2. Async Thunks (for API calls)
export const fetchTechnicianWorkload = createAsyncThunk(
  'appointments/fetchTechnicianWorkload',
  async () => {
    const response = await api.get('/api/shop/technicians/workload/');
    return response.data;
  }
);

export const assignTechnician = createAsyncThunk(
  'appointments/assignTechnician',
  async ({ appointmentId, technicianId }) => {
    const response = await api.post(`/api/shop/appointments/${appointmentId}/assign-technician/`, {
      technician_id: technicianId
    });
    return response.data;
  }
);

export const startWork = createAsyncThunk(
  'appointments/startWork',
  async (appointmentId) => {
    const response = await api.post(`/api/shop/appointments/${appointmentId}/start-work/`);
    return response.data;
  }
);

export const completeWork = createAsyncThunk(
  'appointments/completeWork',
  async (appointmentId) => {
    const response = await api.post(`/api/shop/appointments/${appointmentId}/complete-work/`);
    return response.data;
  }
);

// 3. Selectors
export const selectAppointmentsByStatus = (state, status) => 
  state.appointments.appointments.filter(apt => apt.status === status);

export const selectAvailableTechnicians = (state) => 
  state.appointments.technicians.filter(tech => tech.workload.is_available);

export const selectPendingAppointments = (state) => 
  state.appointments.appointments.filter(apt => apt.status === 'pending');
```

### 3. React Component Examples

> **📝 NOTE**: These are sample React components for reference. Adapt the patterns, props, and state management to match your existing component architecture and Redux implementation.

#### AppointmentCard Component
```tsx
import React from 'react';
import { useDispatch } from 'react-redux';

interface AppointmentCardProps {
  appointment: Appointment;
}

const AppointmentCard: React.FC<AppointmentCardProps> = ({ appointment }) => {
  const dispatch = useDispatch();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-blue-100 text-blue-800';
      case 'assigned': return 'bg-yellow-100 text-yellow-800';
      case 'in_progress': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-red-100 text-red-800';
    }
  };

  const handleAssignTechnician = (technicianId: number) => {
    dispatch(assignTechnician({ appointmentId: appointment.id, technicianId }));
  };

  const handleStartWork = () => {
    dispatch(startWork(appointment.id));
  };

  const handleCompleteWork = () => {
    dispatch(completeWork(appointment.id));
  };

  const getStatusActions = () => {
    switch (appointment.status) {
      case 'pending':
        return (
          <TechnicianSelector 
            onSelect={handleAssignTechnician}
          />
        );
      case 'assigned':
        return (
          <button 
            onClick={handleStartWork}
            className="btn btn-primary"
          >
            Start Work
          </button>
        );
      case 'in_progress':
        return (
          <button 
            onClick={handleCompleteWork}
            className="btn btn-success"
          >
            Complete Work
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div className="appointment-card">
      <div className="flex justify-between items-start">
        <div>
          <h3>{appointment.customer_name}</h3>
          <p>{appointment.vehicle.year} {appointment.vehicle.make} {appointment.vehicle.model}</p>
          <p className="text-sm text-gray-600">{appointment.vehicle.license_plate}</p>
        </div>
        
        <span className={`px-2 py-1 rounded text-sm ${getStatusColor(appointment.status)}`}>
          {appointment.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>
      
      {appointment.assigned_technician && (
        <div className="mt-2">
          <p className="text-sm">
            <strong>Technician:</strong> {appointment.assigned_technician.name}
          </p>
          {appointment.assigned_at && (
            <p className="text-xs text-gray-500">
              Assigned: {new Date(appointment.assigned_at).toLocaleString()}
            </p>
          )}
        </div>
      )}
      
      <div className="mt-3">
        {getStatusActions()}
      </div>
    </div>
  );
};
```

#### TechnicianWorkloadDashboard Component
```tsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

const TechnicianWorkloadDashboard: React.FC = () => {
  const dispatch = useDispatch();
  const { technicians, loading } = useSelector(state => state.appointments);

  useEffect(() => {
    dispatch(fetchTechnicianWorkload());
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      dispatch(fetchTechnicianWorkload());
    }, 30000);
    
    return () => clearInterval(interval);
  }, [dispatch]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="workload-dashboard">
      <div className="summary-cards">
        <div className="card">
          <h3>Total Technicians</h3>
          <p className="text-2xl font-bold">{technicians.length}</p>
        </div>
        <div className="card">
          <h3>Available</h3>
          <p className="text-2xl font-bold text-green-600">
            {technicians.filter(t => t.workload.is_available).length}
          </p>
        </div>
        <div className="card">
          <h3>Busy</h3>
          <p className="text-2xl font-bold text-red-600">
            {technicians.filter(t => !t.workload.is_available).length}
          </p>
        </div>
      </div>

      <div className="technician-list">
        {technicians.map(tech => (
          <div key={tech.technician.id} className="technician-card">
            <div className="flex justify-between items-center">
              <div>
                <h4>{tech.technician.name}</h4>
                <p className="text-sm text-gray-600">{tech.technician.role}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold">
                  {tech.workload.current_appointments}/{tech.workload.max_capacity}
                </p>
                <span className={`px-2 py-1 rounded text-xs ${
                  tech.workload.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {tech.workload.is_available ? 'Available' : 'Busy'}
                </span>
              </div>
            </div>
            
            {tech.current_jobs.length > 0 && (
              <div className="mt-2">
                <p className="text-sm font-medium">Current Jobs:</p>
                <ul className="text-xs text-gray-600">
                  {tech.current_jobs.map(job => (
                    <li key={job.appointment_id}>
                      #{job.appointment_id}: {job.customer} - {job.vehicle} ({job.status})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 🔄 WORKFLOW IMPLEMENTATION

### Status Transition Logic
```javascript
// Status transition helpers
const canAssignTechnician = (appointment) => {
  return appointment.status === 'pending';
};

const canStartWork = (appointment) => {
  return appointment.status === 'assigned' && appointment.assigned_technician;
};

const canCompleteWork = (appointment) => {
  return appointment.status === 'in_progress';
};

// Workflow validation
const validateStatusTransition = (currentStatus, newStatus) => {
  const validTransitions = {
    'pending': ['assigned', 'cancelled'],
    'assigned': ['in_progress', 'cancelled'],
    'in_progress': ['completed', 'cancelled'],
    'completed': [],
    'cancelled': []
  };
  
  return validTransitions[currentStatus]?.includes(newStatus) || false;
};
```

---

## 🎯 QUESTIONS FOR FRONTEND DEVELOPER

### Implementation Feedback Needed

1. **Technician Assignment UI**
   - How do you envision the technician assignment interface?
   - Should it be a dropdown, modal, or drag-and-drop?
   - Do you need batch assignment capabilities?
   - Should UI filter employees by role or show all employees?

2. **Real-time Updates**
   - Do you need WebSocket/SSE for real-time status updates?
   - How often should workload data refresh (currently 30 seconds)?

3. **Error Handling**
   - How do you prefer error handling in your Redux architecture?
   - What error scenarios need specific handling?

4. **Additional Features**
   - Do you need bulk operations (assign multiple appointments)?
   - Should we add appointment filtering by technician?
   - Do you need historical workload data?

5. **Mobile Considerations**
   - Will technicians use mobile devices to update status?
   - Do you need simplified mobile APIs?

6. **Workload Management**
   - Is the 3-appointment limit per technician appropriate?
   - Should this be configurable per technician or shop?

---

## 📞 NEXT STEPS

### Integration Checklist
- [ ] Review and adapt TypeScript interfaces
- [ ] Integrate Redux actions and reducers for technician assignment
- [ ] Implement technician assignment UI components
- [ ] Add appointment status workflow to existing views
- [ ] Test technician assignment workflow end-to-end
- [ ] Implement workload dashboard (optional)

### Testing Endpoints
- Test at: `http://127.0.0.1:8000/api/shop/`
- Available endpoints:
  - `POST /appointments/{id}/assign-technician/`
  - `POST /appointments/{id}/start-work/`
  - `POST /appointments/{id}/complete-work/`
  - `GET /technicians/workload/`
  - `GET /technicians/available/`

---

## ✅ SYSTEM STATUS

**Technician Assignment System**: ✅ Complete and tested
- **5 new API endpoints**: All functional
- **Database schema**: Enhanced with technician fields and timestamps
- **Workflow logic**: pending → assigned → in_progress → completed
- **Workload management**: Real-time tracking with 3-appointment limit per technician

**Ready for frontend integration!** 🎯
