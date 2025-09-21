# Technician Management & Workload Frontend Guide
## Complete Implementation Guide for Technician-Related Features

> **🎯 FOCUSED**: Comprehensive guide specifically for technician management, workload tracking, and assignment workflows

---

## Table of Contents
1. [Technician Data Structure](#technician-data-structure)
2. [Core API Endpoints](#core-api-endpoints)
3. [Real-Time Workload Management](#real-time-workload-management)
4. [Assignment Workflows](#assignment-workflows)
5. [TypeScript Interfaces](#typescript-interfaces)
6. [React Components](#react-components)
7. [Redux State Management](#redux-state-management)
8. [WebSocket Integration](#websocket-integration)
9. [Performance Optimization](#performance-optimization)

---

## Technician Data Structure

### Enhanced Employee/Technician Response
**✅ Verified Live Response** from `/api/shop/employees/`:

```json
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
```

### Key Computed Properties
- **`workload_count`**: Number of active assignments
- **`is_available`**: Boolean availability status
- **`appointments_today_count`**: Today's scheduled appointments
- **`is_technician`**: Role-based filter flag
- **`current_jobs`**: Array of active job assignments

---

## Core API Endpoints

### 1. Get All Technicians
```http
GET /api/shop/employees/?role=technician
Authorization: Bearer {token}
```

**Filter Options**:
```http
GET /api/shop/employees/?role=technician&is_available=true
GET /api/shop/employees/?role=technician&workload_count__lte=2
```

### 2. Technician Workload Overview
```http
GET /api/shop/technicians/workload/
Authorization: Bearer {token}
```

**✅ Verified Response**:
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

### 3. Assignment Operations
```http
# Assign technician to appointment
POST /api/shop/appointments/{appointment_id}/assign-technician/
{
  "technician_id": 27
}

# Start work
POST /api/shop/appointments/{appointment_id}/start-work/

# Complete work  
POST /api/shop/appointments/{appointment_id}/complete-work/

# Unassign technician
POST /api/shop/appointments/{appointment_id}/unassign-technician/
```

---

## Real-Time Workload Management

### Workload Polling Strategy
```javascript
// Recommended polling intervals
const POLLING_INTERVALS = {
  workload: 30000,      // 30 seconds - moderate priority
  assignments: 15000,   // 15 seconds - high priority  
  dashboard: 60000      // 1 minute - lower priority
};

class WorkloadManager {
  constructor() {
    this.intervals = new Map();
  }

  startPolling() {
    // Poll workload data
    this.intervals.set('workload', setInterval(async () => {
      await this.fetchWorkloadData();
    }, POLLING_INTERVALS.workload));

    // Poll assignment updates
    this.intervals.set('assignments', setInterval(async () => {
      await this.fetchAssignmentUpdates();
    }, POLLING_INTERVALS.assignments));
  }

  async fetchWorkloadData() {
    try {
      const response = await api.get('/shop/technicians/workload/');
      store.dispatch(updateWorkloadData(response.data));
    } catch (error) {
      console.error('Workload fetch failed:', error);
    }
  }

  stopPolling() {
    this.intervals.forEach(interval => clearInterval(interval));
    this.intervals.clear();
  }
}
```

### Smart Caching Strategy
```javascript
class TechnicianCache {
  constructor() {
    this.cache = new Map();
    this.lastUpdated = new Map();
    this.CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  }

  async getTechnicians(forceRefresh = false) {
    const cacheKey = 'technicians';
    const now = Date.now();
    
    if (!forceRefresh && 
        this.cache.has(cacheKey) && 
        (now - this.lastUpdated.get(cacheKey)) < this.CACHE_DURATION) {
      return this.cache.get(cacheKey);
    }

    const data = await api.get('/shop/employees/?role=technician');
    this.cache.set(cacheKey, data);
    this.lastUpdated.set(cacheKey, now);
    return data;
  }

  invalidateCache(key = null) {
    if (key) {
      this.cache.delete(key);
      this.lastUpdated.delete(key);
    } else {
      this.cache.clear();
      this.lastUpdated.clear();
    }
  }
}
```

---

## Assignment Workflows

### Automatic Assignment Logic
```javascript
class AutoAssignmentService {
  constructor(technicians) {
    this.technicians = technicians;
  }

  findBestTechnician(appointment) {
    const availableTechnicians = this.technicians.filter(tech => 
      tech.is_available && tech.workload_count < 3
    );

    if (availableTechnicians.length === 0) {
      return null; // No available technicians
    }

    // Sort by workload (ascending) and experience
    return availableTechnicians.sort((a, b) => {
      if (a.workload_count !== b.workload_count) {
        return a.workload_count - b.workload_count;
      }
      // Secondary sort by experience or other criteria
      return b.experience_years - a.experience_years;
    })[0];
  }

  async autoAssign(appointmentId) {
    const bestTechnician = this.findBestTechnician();
    
    if (!bestTechnician) {
      throw new Error('No available technicians');
    }

    return await api.post(`/shop/appointments/${appointmentId}/assign-technician/`, {
      technician_id: bestTechnician.id
    });
  }
}
```

### Manual Assignment Workflow
```javascript
class ManualAssignmentWorkflow {
  constructor() {
    this.selectedAppointment = null;
    this.availableTechnicians = [];
  }

  async initiateAssignment(appointmentId) {
    this.selectedAppointment = await api.get(`/shop/appointments/${appointmentId}/`);
    this.availableTechnicians = await this.getAvailableTechnicians();
    return {
      appointment: this.selectedAppointment,
      technicians: this.availableTechnicians
    };
  }

  async getAvailableTechnicians() {
    const response = await api.get('/shop/employees/?role=technician');
    return response.data.filter(tech => tech.is_available);
  }

  async confirmAssignment(technicianId) {
    const result = await api.post(
      `/shop/appointments/${this.selectedAppointment.id}/assign-technician/`,
      { technician_id: technicianId }
    );
    
    // Update local state
    this.selectedAppointment = null;
    return result;
  }
}
```

---

## TypeScript Interfaces

```typescript
// Core interfaces
interface Technician {
  id: number;
  name: string;
  role: 'technician' | 'manager' | 'owner';
  phone_number: string;
  email: string;
  picture?: string;
  shop: number;
  user?: number;
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
  status: 'assigned' | 'in_progress' | 'completed';
  date: string;
  assigned_at: string;
  started_at?: string;
}

interface WorkloadOverview {
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

interface AssignmentRequest {
  technician_id: number;
}

interface AssignmentResponse {
  id: number;
  assigned_technician: Technician;
  assigned_at: string;
  status: string;
}

// API Response types
type TechniciansResponse = Technician[];
type WorkloadResponse = WorkloadOverview;
type AssignmentApiResponse = AssignmentResponse;

// Component Props
interface TechnicianCardProps {
  technician: Technician;
  onAssign: (technicianId: number) => void;
  isSelectable?: boolean;
  showWorkload?: boolean;
}

interface WorkloadDashboardProps {
  workloadData: WorkloadOverview;
  onRefresh: () => void;
  autoRefresh?: boolean;
}

interface AssignmentModalProps {
  isOpen: boolean;
  appointment: Appointment;
  technicians: Technician[];
  onAssign: (technicianId: number) => Promise<void>;
  onClose: () => void;
}
```

---

## React Components

### Technician Card Component
```tsx
import React from 'react';
import { Technician } from '../types';

interface TechnicianCardProps {
  technician: Technician;
  onAssign?: (technicianId: number) => void;
  isSelectable?: boolean;
  showActions?: boolean;
}

const TechnicianCard: React.FC<TechnicianCardProps> = ({
  technician,
  onAssign,
  isSelectable = false,
  showActions = true
}) => {
  const getStatusColor = () => {
    if (!technician.is_available) return 'bg-red-100 text-red-800';
    if (technician.workload_count === 0) return 'bg-green-100 text-green-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getStatusText = () => {
    if (!technician.is_available) return 'Unavailable';
    if (technician.workload_count === 0) return 'Available';
    return `${technician.workload_count} job${technician.workload_count > 1 ? 's' : ''}`;
  };

  return (
    <div className={`p-4 border rounded-lg ${isSelectable ? 'cursor-pointer hover:bg-gray-50' : ''}`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-lg">{technician.name}</h3>
          <p className="text-gray-600 text-sm">{technician.email}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>

      {/* Workload Info */}
      <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
        <div>
          <span className="text-gray-500">Active Jobs:</span>
          <span className="ml-2 font-medium">{technician.workload_count}</span>
        </div>
        <div>
          <span className="text-gray-500">Today's Appointments:</span>
          <span className="ml-2 font-medium">{technician.appointments_today_count}</span>
        </div>
      </div>

      {/* Current Jobs */}
      {technician.current_jobs.length > 0 && (
        <div className="mb-3">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Current Jobs:</h4>
          <div className="space-y-2">
            {technician.current_jobs.map((job) => (
              <div key={job.appointment_id} className="text-xs bg-gray-50 p-2 rounded">
                <div className="font-medium">{job.vehicle}</div>
                <div className="text-gray-600">{job.customer}</div>
                <div className="flex justify-between mt-1">
                  <span className={`px-1 rounded text-xs ${
                    job.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {job.status.replace('_', ' ')}
                  </span>
                  <span className="text-gray-500">
                    {new Date(job.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      {showActions && onAssign && (
        <div className="flex gap-2">
          <button
            onClick={() => onAssign(technician.id)}
            disabled={!technician.is_available}
            className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Assign Job
          </button>
          <button className="px-3 py-2 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50">
            View Details
          </button>
        </div>
      )}
    </div>
  );
};

export default TechnicianCard;
```

### Workload Dashboard Component
```tsx
import React, { useState, useEffect } from 'react';
import { WorkloadOverview } from '../types';
import TechnicianCard from './TechnicianCard';

interface WorkloadDashboardProps {
  onAssign: (technicianId: number) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const WorkloadDashboard: React.FC<WorkloadDashboardProps> = ({
  onAssign,
  autoRefresh = true,
  refreshInterval = 30000
}) => {
  const [workloadData, setWorkloadData] = useState<WorkloadOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchWorkloadData = async () => {
    try {
      const response = await fetch('/api/shop/technicians/workload/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setWorkloadData(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch workload data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkloadData();

    if (autoRefresh) {
      const interval = setInterval(fetchWorkloadData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  if (loading) {
    return <div className="flex justify-center p-8">Loading workload data...</div>;
  }

  if (!workloadData) {
    return <div className="text-center p-8 text-gray-500">No workload data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Technician Workload Overview</h2>
          <div className="flex items-center gap-4">
            {lastUpdated && (
              <span className="text-sm text-gray-500">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <button
              onClick={fetchWorkloadData}
              className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {workloadData.summary.total_technicians}
            </div>
            <div className="text-sm text-blue-800">Total Technicians</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded">
            <div className="text-2xl font-bold text-green-600">
              {workloadData.summary.available_technicians}
            </div>
            <div className="text-sm text-green-800">Available</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded">
            <div className="text-2xl font-bold text-yellow-600">
              {workloadData.summary.busy_technicians}
            </div>
            <div className="text-sm text-yellow-800">Busy</div>
          </div>
        </div>
      </div>

      {/* Technician Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workloadData.technicians.map((technicianWorkload) => {
          const technician = {
            ...technicianWorkload.technician,
            workload_count: technicianWorkload.workload.current_appointments,
            is_available: technicianWorkload.workload.is_available,
            appointments_today_count: technicianWorkload.workload.appointments_today,
            is_technician: true,
            current_jobs: technicianWorkload.current_jobs,
            phone_number: '',
            email: '',
            shop: 0,
          };

          return (
            <TechnicianCard
              key={technician.id}
              technician={technician}
              onAssign={onAssign}
              showActions={true}
            />
          );
        })}
      </div>
    </div>
  );
};

export default WorkloadDashboard;
```

### Assignment Modal Component
```tsx
import React, { useState } from 'react';
import { Appointment, Technician } from '../types';

interface AssignmentModalProps {
  isOpen: boolean;
  appointment: Appointment;
  technicians: Technician[];
  onAssign: (technicianId: number) => Promise<void>;
  onClose: () => void;
}

const AssignmentModal: React.FC<AssignmentModalProps> = ({
  isOpen,
  appointment,
  technicians,
  onAssign,
  onClose
}) => {
  const [selectedTechnicianId, setSelectedTechnicianId] = useState<number | null>(null);
  const [isAssigning, setIsAssigning] = useState(false);

  const handleAssign = async () => {
    if (!selectedTechnicianId) return;

    setIsAssigning(true);
    try {
      await onAssign(selectedTechnicianId);
      onClose();
    } catch (error) {
      console.error('Assignment failed:', error);
    } finally {
      setIsAssigning(false);
    }
  };

  if (!isOpen) return null;

  const availableTechnicians = technicians.filter(tech => tech.is_available);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Assign Technician</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {/* Appointment Details */}
        <div className="bg-gray-50 p-4 rounded mb-4">
          <h3 className="font-medium mb-2">Appointment Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Vehicle:</span>
              <span className="ml-2">{appointment.vehicle?.make} {appointment.vehicle?.model}</span>
            </div>
            <div>
              <span className="text-gray-500">Customer:</span>
              <span className="ml-2">{appointment.customer_name}</span>
            </div>
            <div>
              <span className="text-gray-500">Date:</span>
              <span className="ml-2">
                {new Date(appointment.date).toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Description:</span>
              <span className="ml-2">{appointment.description}</span>
            </div>
          </div>
        </div>

        {/* Technician Selection */}
        <div className="mb-6">
          <h3 className="font-medium mb-3">Available Technicians</h3>
          
          {availableTechnicians.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              No available technicians
            </div>
          ) : (
            <div className="space-y-3">
              {availableTechnicians.map((technician) => (
                <div
                  key={technician.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTechnicianId === technician.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedTechnicianId(technician.id)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{technician.name}</div>
                      <div className="text-sm text-gray-600">{technician.email}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">
                        Workload: {technician.workload_count} job{technician.workload_count !== 1 ? 's' : ''}
                      </div>
                      <div className="text-sm text-gray-500">
                        Today: {technician.appointments_today_count} appointments
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleAssign}
            disabled={!selectedTechnicianId || isAssigning || availableTechnicians.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isAssigning ? 'Assigning...' : 'Assign Technician'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssignmentModal;
```

---

## Redux State Management

### State Structure
```typescript
interface TechnicianState {
  technicians: Technician[];
  workloadData: WorkloadOverview | null;
  selectedTechnician: Technician | null;
  assignments: Assignment[];
  loading: {
    technicians: boolean;
    workload: boolean;
    assignment: boolean;
  };
  error: string | null;
  lastUpdated: {
    technicians: number | null;
    workload: number | null;
  };
}

const initialState: TechnicianState = {
  technicians: [],
  workloadData: null,
  selectedTechnician: null,
  assignments: [],
  loading: {
    technicians: false,
    workload: false,
    assignment: false,
  },
  error: null,
  lastUpdated: {
    technicians: null,
    workload: null,
  },
};
```

### Actions
```typescript
// Action Types
const TECHNICIAN_ACTIONS = {
  FETCH_TECHNICIANS_START: 'FETCH_TECHNICIANS_START',
  FETCH_TECHNICIANS_SUCCESS: 'FETCH_TECHNICIANS_SUCCESS',
  FETCH_TECHNICIANS_ERROR: 'FETCH_TECHNICIANS_ERROR',
  
  FETCH_WORKLOAD_START: 'FETCH_WORKLOAD_START',
  FETCH_WORKLOAD_SUCCESS: 'FETCH_WORKLOAD_SUCCESS',
  FETCH_WORKLOAD_ERROR: 'FETCH_WORKLOAD_ERROR',
  
  ASSIGN_TECHNICIAN_START: 'ASSIGN_TECHNICIAN_START',
  ASSIGN_TECHNICIAN_SUCCESS: 'ASSIGN_TECHNICIAN_SUCCESS',
  ASSIGN_TECHNICIAN_ERROR: 'ASSIGN_TECHNICIAN_ERROR',
  
  UPDATE_TECHNICIAN_WORKLOAD: 'UPDATE_TECHNICIAN_WORKLOAD',
  SET_SELECTED_TECHNICIAN: 'SET_SELECTED_TECHNICIAN',
  CLEAR_ERROR: 'CLEAR_ERROR',
} as const;

// Action Creators
export const fetchTechnicians = () => async (dispatch: Dispatch) => {
  dispatch({ type: TECHNICIAN_ACTIONS.FETCH_TECHNICIANS_START });
  
  try {
    const response = await api.get('/shop/employees/?role=technician');
    dispatch({
      type: TECHNICIAN_ACTIONS.FETCH_TECHNICIANS_SUCCESS,
      payload: {
        technicians: response.data,
        timestamp: Date.now(),
      },
    });
  } catch (error) {
    dispatch({
      type: TECHNICIAN_ACTIONS.FETCH_TECHNICIANS_ERROR,
      payload: error.message,
    });
  }
};

export const fetchWorkloadData = () => async (dispatch: Dispatch) => {
  dispatch({ type: TECHNICIAN_ACTIONS.FETCH_WORKLOAD_START });
  
  try {
    const response = await api.get('/shop/technicians/workload/');
    dispatch({
      type: TECHNICIAN_ACTIONS.FETCH_WORKLOAD_SUCCESS,
      payload: {
        workloadData: response.data,
        timestamp: Date.now(),
      },
    });
  } catch (error) {
    dispatch({
      type: TECHNICIAN_ACTIONS.FETCH_WORKLOAD_ERROR,
      payload: error.message,
    });
  }
};

export const assignTechnician = (appointmentId: number, technicianId: number) => 
  async (dispatch: Dispatch) => {
    dispatch({ type: TECHNICIAN_ACTIONS.ASSIGN_TECHNICIAN_START });
    
    try {
      const response = await api.post(
        `/shop/appointments/${appointmentId}/assign-technician/`,
        { technician_id: technicianId }
      );
      
      dispatch({
        type: TECHNICIAN_ACTIONS.ASSIGN_TECHNICIAN_SUCCESS,
        payload: response.data,
      });
      
      // Refresh workload data after assignment
      dispatch(fetchWorkloadData());
      
    } catch (error) {
      dispatch({
        type: TECHNICIAN_ACTIONS.ASSIGN_TECHNICIAN_ERROR,
        payload: error.message,
      });
    }
  };
```

### Reducer
```typescript
const technicianReducer = (
  state = initialState,
  action: any
): TechnicianState => {
  switch (action.type) {
    case TECHNICIAN_ACTIONS.FETCH_TECHNICIANS_START:
      return {
        ...state,
        loading: { ...state.loading, technicians: true },
        error: null,
      };

    case TECHNICIAN_ACTIONS.FETCH_TECHNICIANS_SUCCESS:
      return {
        ...state,
        technicians: action.payload.technicians,
        loading: { ...state.loading, technicians: false },
        lastUpdated: { ...state.lastUpdated, technicians: action.payload.timestamp },
        error: null,
      };

    case TECHNICIAN_ACTIONS.FETCH_TECHNICIANS_ERROR:
      return {
        ...state,
        loading: { ...state.loading, technicians: false },
        error: action.payload,
      };

    case TECHNICIAN_ACTIONS.FETCH_WORKLOAD_START:
      return {
        ...state,
        loading: { ...state.loading, workload: true },
        error: null,
      };

    case TECHNICIAN_ACTIONS.FETCH_WORKLOAD_SUCCESS:
      return {
        ...state,
        workloadData: action.payload.workloadData,
        loading: { ...state.loading, workload: false },
        lastUpdated: { ...state.lastUpdated, workload: action.payload.timestamp },
        error: null,
      };

    case TECHNICIAN_ACTIONS.ASSIGN_TECHNICIAN_START:
      return {
        ...state,
        loading: { ...state.loading, assignment: true },
        error: null,
      };

    case TECHNICIAN_ACTIONS.ASSIGN_TECHNICIAN_SUCCESS:
      return {
        ...state,
        loading: { ...state.loading, assignment: false },
        // Update local technician data optimistically
        technicians: state.technicians.map(tech => 
          tech.id === action.payload.assigned_technician?.id
            ? { ...tech, workload_count: tech.workload_count + 1, is_available: tech.workload_count + 1 < 3 }
            : tech
        ),
        error: null,
      };

    case TECHNICIAN_ACTIONS.SET_SELECTED_TECHNICIAN:
      return {
        ...state,
        selectedTechnician: action.payload,
      };

    case TECHNICIAN_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};
```

### Selectors
```typescript
// Selectors
export const selectAllTechnicians = (state: RootState) => state.technician.technicians;

export const selectAvailableTechnicians = (state: RootState) =>
  state.technician.technicians.filter(tech => tech.is_available);

export const selectTechnicianById = (state: RootState, technicianId: number) =>
  state.technician.technicians.find(tech => tech.id === technicianId);

export const selectWorkloadData = (state: RootState) => state.technician.workloadData;

export const selectTechnicianLoadingStates = (state: RootState) => state.technician.loading;

export const selectBusyTechnicians = (state: RootState) =>
  state.technician.technicians.filter(tech => !tech.is_available || tech.workload_count > 0);

export const selectTechniciansByWorkload = (state: RootState) =>
  [...state.technician.technicians].sort((a, b) => a.workload_count - b.workload_count);

// Memoized selectors using reselect
import { createSelector } from 'reselect';

export const selectTechnicianStats = createSelector(
  [selectAllTechnicians],
  (technicians) => ({
    total: technicians.length,
    available: technicians.filter(tech => tech.is_available).length,
    busy: technicians.filter(tech => !tech.is_available || tech.workload_count > 0).length,
    averageWorkload: technicians.length > 0 
      ? technicians.reduce((sum, tech) => sum + tech.workload_count, 0) / technicians.length 
      : 0,
  })
);
```

---

## WebSocket Integration

### Real-Time Updates Setup
```typescript
class TechnicianWebSocketManager {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(private dispatch: Dispatch) {}

  connect() {
    const token = localStorage.getItem('token');
    this.socket = new WebSocket(`ws://localhost:8000/ws/technicians/?token=${token}`);

    this.socket.onopen = () => {
      console.log('Technician WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.socket.onclose = () => {
      console.log('Technician WebSocket disconnected');
      this.attemptReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleMessage(data: any) {
    switch (data.type) {
      case 'workload_update':
        this.dispatch({
          type: 'UPDATE_TECHNICIAN_WORKLOAD',
          payload: data.payload,
        });
        break;

      case 'assignment_created':
        this.dispatch({
          type: 'ASSIGNMENT_CREATED',
          payload: data.payload,
        });
        // Show notification
        this.showNotification(`Assignment created for ${data.payload.technician_name}`);
        break;

      case 'job_started':
        this.dispatch({
          type: 'JOB_STARTED',
          payload: data.payload,
        });
        break;

      case 'job_completed':
        this.dispatch({
          type: 'JOB_COMPLETED',
          payload: data.payload,
        });
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Reconnection attempt ${this.reconnectAttempts}`);
      this.connect();
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
  }

  private showNotification(message: string) {
    // Implement notification system
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Technician Update', { body: message });
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

// Usage in App component
const App = () => {
  const dispatch = useDispatch();
  
  useEffect(() => {
    const wsManager = new TechnicianWebSocketManager(dispatch);
    wsManager.connect();

    return () => wsManager.disconnect();
  }, [dispatch]);

  // ... rest of app
};
```

---

## Performance Optimization

### Memoization Strategies
```typescript
// Memoized technician list component
const TechnicianList = React.memo(({ technicians, onAssign }: {
  technicians: Technician[];
  onAssign: (id: number) => void;
}) => {
  const sortedTechnicians = useMemo(
    () => [...technicians].sort((a, b) => {
      // Sort by availability first, then by workload
      if (a.is_available !== b.is_available) {
        return a.is_available ? -1 : 1;
      }
      return a.workload_count - b.workload_count;
    }),
    [technicians]
  );

  return (
    <div className="space-y-4">
      {sortedTechnicians.map((technician) => (
        <TechnicianCard
          key={technician.id}
          technician={technician}
          onAssign={onAssign}
        />
      ))}
    </div>
  );
});

// Optimized hooks
const useTechnicianData = () => {
  const dispatch = useDispatch();
  const technicians = useSelector(selectAllTechnicians);
  const workloadData = useSelector(selectWorkloadData);
  const loading = useSelector(selectTechnicianLoadingStates);

  const refreshTechnicians = useCallback(() => {
    dispatch(fetchTechnicians());
  }, [dispatch]);

  const refreshWorkload = useCallback(() => {
    dispatch(fetchWorkloadData());
  }, [dispatch]);

  const assignTechnicianToJob = useCallback((appointmentId: number, technicianId: number) => {
    return dispatch(assignTechnician(appointmentId, technicianId));
  }, [dispatch]);

  return {
    technicians,
    workloadData,
    loading,
    refreshTechnicians,
    refreshWorkload,
    assignTechnicianToJob,
  };
};
```

### Virtual Scrolling for Large Lists
```typescript
import { FixedSizeList as List } from 'react-window';

const VirtualTechnicianList = ({ technicians, onAssign }: {
  technicians: Technician[];
  onAssign: (id: number) => void;
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <TechnicianCard
        technician={technicians[index]}
        onAssign={onAssign}
      />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={technicians.length}
      itemSize={200}
      itemData={technicians}
    >
      {Row}
    </List>
  );
};
```

---

## Implementation Checklist

### ✅ Essential Features
- [ ] Fetch and display technician list with computed properties
- [ ] Real-time workload monitoring
- [ ] Manual technician assignment workflow
- [ ] Automatic assignment algorithm
- [ ] Job status tracking (assigned → in_progress → completed)
- [ ] Optimistic UI updates
- [ ] Error handling and retry logic
- [ ] Responsive design for mobile/tablet

### 🚀 Advanced Features  
- [ ] WebSocket integration for real-time updates
- [ ] Push notifications for assignment changes
- [ ] Drag-and-drop assignment interface
- [ ] Technician performance analytics
- [ ] Workload prediction and optimization
- [ ] Offline support with sync
- [ ] Advanced filtering and search
- [ ] Export functionality for reports

### 🔧 Performance Optimizations
- [ ] Component memoization
- [ ] Virtual scrolling for large datasets
- [ ] Debounced search inputs
- [ ] Optimized re-renders
- [ ] Lazy loading for technician details
- [ ] Image optimization for technician photos
- [ ] Bundle splitting for technician modules

---

This comprehensive guide provides everything needed to implement robust technician management and workload assignment features in your frontend application! 🎯