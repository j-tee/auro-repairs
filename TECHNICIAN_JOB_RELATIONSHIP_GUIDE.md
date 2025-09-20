# 🔧 TECHNICIAN-REPAIR JOB RELATIONSHIP
## Detailed System Architecture & Data Flow

### 📋 Overview
This document provides a **detailed explanation** of how technicians are connected to repair jobs in the system, the data relationships, workflow processes, and how the frontend should handle technician-job assignments.

---

## 🏗️ SYSTEM ARCHITECTURE

### Entity Relationship Overview
```
Customer ──┐
           ├── Vehicle ──── Appointment ──── Employee (Technician)
           │                    │
           │                    └── RepairOrder ──── Employee (Technician)
           │
           └── RepairOrder ──── Employee (Technician)
```

### Core Entities and Their Role in Technician Assignment

#### 1. **Employee (Technician)**
```javascript
// Employee model - represents all shop staff
{
  id: 5,
  name: "John Smith",
  role: "technician",        // Determines if they can be assigned to jobs
  phone_number: "+1234567890",
  email: "john@shop.com",
  
  // Computed properties for workload management
  current_appointments: 2,    // Active appointments assigned
  workload_count: 2,         // Same as current_appointments
  is_available: true,        // Can take more jobs (< 3 appointments)
  appointments_today: 3      // Today's total appointments
}
```

#### 2. **Appointment (Service Booking)**
```javascript
// Appointment - when customer books service
{
  id: 27,
  customer_id: 19,
  customer_name: "Alice Cooper",
  vehicle_id: 27,
  vehicle: { make: "Toyota", model: "Camry", license_plate: "ABC-123" },
  
  // 🎯 TECHNICIAN ASSIGNMENT FIELDS
  assigned_technician_id: 5,     // WHO: Employee ID of assigned technician
  assigned_technician: {         // WHO: Full technician details
    id: 5,
    name: "John Smith", 
    role: "technician"
  },
  
  // 🎯 WORKFLOW TRACKING FIELDS  
  assigned_at: "2025-09-13T09:44:37Z",  // WHEN: Technician was assigned
  started_at: "2025-09-13T10:15:22Z",   // WHEN: Work actually began
  completed_at: null,                    // WHEN: Work finished (null = ongoing)
  
  // 🎯 JOB STATUS
  status: "in_progress",        // WHAT STAGE: pending/assigned/in_progress/completed
  date: "2025-09-13T08:00:00Z", // WHEN: Customer's scheduled time
  description: "Engine noise inspection"  // WHAT WORK: Job description
}
```

#### 3. **RepairOrder (Work Order)**
```javascript
// RepairOrder - detailed work breakdown (created from appointment)
{
  id: 9,
  appointment_id: 27,        // Links back to the appointment
  customer_id: 19,
  vehicle_id: 27,
  
  // 🎯 TECHNICIAN ASSIGNMENT (same as appointment)
  assigned_technician_id: 5,  // Same technician as appointment
  assigned_technician: {      // Same technician details
    id: 5,
    name: "John Smith",
    role: "technician"
  },
  
  // 🎯 WORK DETAILS
  total_cost: 450.00,
  labor_cost: 200.00,
  parts_cost: 250.00,
  status: "in_progress",
  
  // 🎯 WORK ITEMS (what technician needs to do)
  repair_items: [
    {
      description: "Replace brake pads",
      labor_hours: 2.0,
      cost: 150.00,
      status: "in_progress"
    },
    {
      description: "Oil change",
      labor_hours: 0.5,
      cost: 50.00, 
      status: "completed"
    }
  ]
}
```

---

## 🔄 TECHNICIAN-JOB ASSIGNMENT WORKFLOW

### Step-by-Step Process

#### **Step 1: Customer Books Appointment**
```javascript
// Initial appointment creation
const newAppointment = {
  id: 27,
  customer_id: 19,
  vehicle_id: 27,
  date: "2025-09-13T08:00:00Z",
  description: "Engine noise inspection",
  
  // 🎯 NO TECHNICIAN ASSIGNED YET
  assigned_technician_id: null,
  assigned_technician: null,
  assigned_at: null,
  started_at: null,
  completed_at: null,
  status: "pending"  // Waiting for technician assignment
};
```

#### **Step 2: Shop Manager Assigns Technician**
```javascript
// API call to assign technician
POST /api/shop/appointments/27/assign-technician/
{
  "technician_id": 5  // Employee ID of John Smith
}

// Result: Appointment updated
const updatedAppointment = {
  id: 27,
  // ... other fields stay same
  
  // 🎯 TECHNICIAN NOW ASSIGNED
  assigned_technician_id: 5,
  assigned_technician: {
    id: 5,
    name: "John Smith",
    role: "technician"
  },
  assigned_at: "2025-09-13T09:44:37Z",  // Timestamp of assignment
  status: "assigned"  // Status changed from pending → assigned
};
```

#### **Step 3: Technician Starts Work**
```javascript
// Technician (or manager) marks work as started
POST /api/shop/appointments/27/start-work/

// Result: Status and timeline updated
const workStartedAppointment = {
  id: 27,
  // ... technician assignment stays same
  assigned_technician_id: 5,
  assigned_technician: { id: 5, name: "John Smith", role: "technician" },
  assigned_at: "2025-09-13T09:44:37Z",
  
  // 🎯 WORK TIMELINE TRACKING
  started_at: "2025-09-13T10:15:22Z",  // When work actually began
  completed_at: null,                   // Still working
  status: "in_progress"  // Status changed from assigned → in_progress
};
```

#### **Step 4: RepairOrder Created (Optional)**
```javascript
// System creates detailed work order
const repairOrder = {
  id: 9,
  appointment_id: 27,  // Links to the appointment
  
  // 🎯 INHERITS TECHNICIAN FROM APPOINTMENT
  assigned_technician_id: 5,      // Same as appointment
  assigned_technician: {          // Same as appointment
    id: 5,
    name: "John Smith", 
    role: "technician"
  },
  
  // 🎯 DETAILED WORK BREAKDOWN
  repair_items: [
    { description: "Diagnose engine noise", status: "in_progress" },
    { description: "Replace faulty component", status: "pending" }
  ],
  status: "in_progress"
};
```

#### **Step 5: Work Completion**
```javascript
// Technician completes all work
POST /api/shop/appointments/27/complete-work/

// Result: Final status update
const completedAppointment = {
  id: 27,
  // ... all previous fields stay same
  assigned_technician_id: 5,
  assigned_technician: { id: 5, name: "John Smith", role: "technician" },
  assigned_at: "2025-09-13T09:44:37Z",
  started_at: "2025-09-13T10:15:22Z",
  
  // 🎯 JOB COMPLETED
  completed_at: "2025-09-13T14:30:15Z",  // When work finished
  status: "completed"  // Final status
};
```

---

## 📊 TECHNICIAN WORKLOAD MANAGEMENT

### How the System Tracks "Who Does What"

#### **1. Current Jobs Per Technician**
```javascript
// API endpoint: GET /api/shop/technicians/workload/
{
  "technicians": [
    {
      "technician": {
        "id": 5,
        "name": "John Smith",
        "role": "technician"
      },
      "workload": {
        "current_appointments": 2,      // How many jobs assigned
        "is_available": true,           // Can take more jobs?
        "max_capacity": 3,              // Maximum concurrent jobs
        "appointments_today": 3         // Today's total workload
      },
      
      // 🎯 DETAILED JOB LIST - Shows exactly what technician is working on
      "current_jobs": [
        {
          "appointment_id": 27,
          "vehicle": "2020 Toyota Camry (ABC-123)",
          "customer": "Alice Cooper",
          "status": "in_progress",
          "assigned_at": "2025-09-13T09:44:37Z",
          "started_at": "2025-09-13T10:15:22Z",
          "description": "Engine noise inspection"
        },
        {
          "appointment_id": 31,
          "vehicle": "2019 Honda Civic (XYZ-789)", 
          "customer": "Bob Johnson",
          "status": "assigned",
          "assigned_at": "2025-09-13T11:20:15Z",
          "started_at": null,  // Not started yet
          "description": "Brake service"
        }
      ]
    }
  ]
}
```

#### **2. Job Assignment Rules**
```javascript
// Business logic for technician assignment
const assignmentRules = {
  // 🎯 AVAILABILITY RULES
  maxConcurrentJobs: 3,              // Each technician can handle max 3 jobs
  onlyTechniciansCanWork: true,      // Only employees with "technician" role
  
  // 🎯 ASSIGNMENT LOGIC
  whoCanBeAssigned: (employee) => {
    return employee.role.toLowerCase().includes('technician') || 
           employee.role.toLowerCase().includes('mechanic');
  },
  
  isAvailable: (employee) => {
    return employee.current_appointments < 3;
  },
  
  // 🎯 WORK PROGRESSION RULES
  canStartWork: (appointment) => {
    return appointment.status === 'assigned' && 
           appointment.assigned_technician !== null;
  },
  
  canCompleteWork: (appointment) => {
    return appointment.status === 'in_progress';
  }
};
```

---

## 🎯 FRONTEND IMPLEMENTATION - "WHO DOES WHAT" UI

### 1. **Appointment Assignment Interface**
```tsx
// Shows which technician is responsible for each appointment
const AppointmentTechnicianView = ({ appointment }) => {
  return (
    <div className="appointment-card">
      <div className="appointment-header">
        <h3>{appointment.customer_name}'s {appointment.vehicle.make} {appointment.vehicle.model}</h3>
        <span className="license-plate">{appointment.vehicle.license_plate}</span>
      </div>
      
      {/* 🎯 TECHNICIAN RESPONSIBILITY SECTION */}
      <div className="technician-assignment">
        {appointment.assigned_technician ? (
          <div className="assigned-tech">
            <div className="tech-info">
              <strong>👤 Assigned to:</strong> {appointment.assigned_technician.name}
              <span className="role-badge">{appointment.assigned_technician.role}</span>
            </div>
            
            {/* 🎯 TIMELINE TRACKING */}
            <div className="work-timeline">
              {appointment.assigned_at && (
                <div className="timeline-item">
                  ✅ Assigned: {new Date(appointment.assigned_at).toLocaleString()}
                </div>
              )}
              {appointment.started_at && (
                <div className="timeline-item">
                  🔧 Started: {new Date(appointment.started_at).toLocaleString()}
                </div>
              )}
              {appointment.completed_at && (
                <div className="timeline-item">
                  ✅ Completed: {new Date(appointment.completed_at).toLocaleString()}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="unassigned">
            <span className="status-warning">⚠️ No technician assigned</span>
            <TechnicianSelector 
              onAssign={(techId) => assignTechnician(appointment.id, techId)}
            />
          </div>
        )}
      </div>
      
      {/* 🎯 JOB STATUS & ACTIONS */}
      <div className="job-status">
        <span className={`status-badge status-${appointment.status}`}>
          {appointment.status.toUpperCase()}
        </span>
        
        {appointment.status === 'assigned' && (
          <button onClick={() => startWork(appointment.id)}>
            Start Work
          </button>
        )}
        
        {appointment.status === 'in_progress' && (
          <button onClick={() => completeWork(appointment.id)}>
            Complete Work
          </button>
        )}
      </div>
    </div>
  );
};
```

### 2. **Technician Workload Dashboard**
```tsx
// Shows what each technician is responsible for
const TechnicianWorkloadDashboard = ({ technicians }) => {
  return (
    <div className="technician-dashboard">
      <h2>Technician Workload - Who's Doing What</h2>
      
      {technicians.map(tech => (
        <div key={tech.technician.id} className="technician-section">
          {/* 🎯 TECHNICIAN HEADER */}
          <div className="tech-header">
            <h3>👤 {tech.technician.name}</h3>
            <div className="workload-status">
              <span className="job-count">
                {tech.workload.current_appointments}/{tech.workload.max_capacity} Jobs
              </span>
              <span className={`availability ${tech.workload.is_available ? 'available' : 'busy'}`}>
                {tech.workload.is_available ? '✅ Available' : '🚨 At Capacity'}
              </span>
            </div>
          </div>
          
          {/* 🎯 CURRENT JOBS LIST */}
          <div className="current-jobs">
            <h4>Current Responsibilities:</h4>
            {tech.current_jobs.length > 0 ? (
              <ul className="job-list">
                {tech.current_jobs.map(job => (
                  <li key={job.appointment_id} className="job-item">
                    <div className="job-details">
                      <strong>#{job.appointment_id}</strong>: {job.customer}
                      <br />
                      <span className="vehicle-info">🚗 {job.vehicle}</span>
                      <br />
                      <span className="job-description">🔧 {job.description}</span>
                    </div>
                    
                    <div className="job-status">
                      <span className={`status-badge status-${job.status}`}>
                        {job.status.toUpperCase()}
                      </span>
                      
                      {/* 🎯 JOB TIMELINE */}
                      <div className="job-timeline">
                        <small>Assigned: {new Date(job.assigned_at).toLocaleString()}</small>
                        {job.started_at && (
                          <small>Started: {new Date(job.started_at).toLocaleString()}</small>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-jobs">No current assignments</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 3. **Job Assignment Selector**
```tsx
// Allows managers to assign jobs to specific technicians
const TechnicianSelector = ({ onAssign, availableOnly = true }) => {
  const [technicians, setTechnicians] = useState([]);
  
  useEffect(() => {
    // Fetch available technicians
    api.get('/api/shop/technicians/available/')
      .then(response => setTechnicians(response.data));
  }, []);
  
  return (
    <div className="technician-selector">
      <label>Assign to Technician:</label>
      <select onChange={(e) => onAssign(parseInt(e.target.value))}>
        <option value="">Select Technician...</option>
        {technicians.map(tech => (
          <option key={tech.id} value={tech.id}>
            👤 {tech.name} 
            {!tech.workload.is_available && ' (Busy - At Capacity)'}
            ({tech.workload.current_appointments}/{tech.workload.max_capacity} jobs)
          </option>
        ))}
      </select>
      
      {/* 🎯 SHOW TECHNICIAN CURRENT WORKLOAD */}
      <div className="assignment-help">
        <small>
          💡 Each technician can handle up to 3 concurrent jobs. 
          Choose based on current workload and availability.
        </small>
      </div>
    </div>
  );
};
```

---

## 🔍 DATA QUERIES - "FINDING WHO DOES WHAT"

### Frontend Data Access Patterns

#### **1. Get All Jobs for a Specific Technician**
```javascript
// Get all work assigned to John Smith (employee_id: 5)
const getTechnicianJobs = async (technicianId) => {
  const response = await api.get(`/api/shop/appointments/?assigned_technician_id=${technicianId}`);
  return response.data;
  
  // Alternative: Use workload endpoint
  const workloadResponse = await api.get('/api/shop/technicians/workload/');
  const technicianData = workloadResponse.data.technicians.find(
    tech => tech.technician.id === technicianId
  );
  return technicianData?.current_jobs || [];
};
```

#### **2. Find Which Technician is Working on a Specific Job**
```javascript
// Get technician details for appointment #27
const getJobTechnician = async (appointmentId) => {
  const response = await api.get(`/api/shop/appointments/${appointmentId}/`);
  const appointment = response.data;
  
  return {
    job: appointment,
    technician: appointment.assigned_technician,  // Can be null if unassigned
    isAssigned: appointment.assigned_technician !== null,
    status: appointment.status,
    timeline: {
      assigned: appointment.assigned_at,
      started: appointment.started_at,
      completed: appointment.completed_at
    }
  };
};
```

#### **3. Get Unassigned Jobs (Need Technician Assignment)**
```javascript
// Find all jobs waiting for technician assignment
const getUnassignedJobs = async () => {
  const response = await api.get('/api/shop/appointments/?status=pending');
  return response.data.filter(appointment => 
    appointment.assigned_technician_id === null
  );
};
```

#### **4. Get Jobs by Status with Technician Info**
```javascript
// Get all in-progress jobs with their assigned technicians
const getActiveJobs = async () => {
  const response = await api.get('/api/shop/appointments/?status=in_progress');
  return response.data.map(appointment => ({
    jobId: appointment.id,
    customer: appointment.customer_name,
    vehicle: `${appointment.vehicle.year} ${appointment.vehicle.make} ${appointment.vehicle.model}`,
    licensePlate: appointment.vehicle.license_plate,
    technician: appointment.assigned_technician.name,
    technicianId: appointment.assigned_technician.id,
    startedAt: appointment.started_at,
    description: appointment.description
  }));
};
```

---

## 📋 BUSINESS RULES SUMMARY

### **Technician-Job Assignment Rules**

1. **🎯 WHO CAN BE ASSIGNED**
   - Only employees with role "technician" or "mechanic"
   - Must have availability (< 3 current jobs)
   - Must be active employee

2. **🎯 WHEN ASSIGNMENTS HAPPEN**
   - Appointments start as "pending" (no technician)
   - Manager assigns technician → status becomes "assigned"
   - Technician starts work → status becomes "in_progress"
   - Technician completes work → status becomes "completed"

3. **🎯 JOB TRACKING**
   - Each appointment can have only ONE assigned technician
   - Technician assignment is tracked with timestamps
   - RepairOrders inherit technician from their appointment
   - Workload is calculated in real-time

4. **🎯 CAPACITY MANAGEMENT**
   - Max 3 concurrent jobs per technician
   - System prevents over-assignment
   - Availability status updates automatically

---

## ✅ SUMMARY

### **The Technician-Repair Job Relationship Explained:**

1. **🎯 APPOINTMENTS** are the primary unit of work assignment
2. **🎯 TECHNICIANS** are employees who get assigned to appointments
3. **🎯 ONE-TO-ONE** relationship: Each appointment has one assigned technician
4. **🎯 WORKFLOW TRACKING** through status changes and timestamps
5. **🎯 WORKLOAD MANAGEMENT** prevents technician overload
6. **🎯 REAL-TIME VISIBILITY** into who is doing what work

**The system ensures clear accountability:** Every repair job has a specific technician responsible for it, with full timeline tracking from assignment to completion! 🎯
