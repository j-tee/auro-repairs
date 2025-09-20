# TECHNICIAN ALLOCATION SCHEMA ENHANCEMENT

## Current Problem
The schema lacks the ability to:
1. **Assign technicians to appointments** - No field connects appointments to employees
2. **Track allocation timestamps** - When was a technician assigned?
3. **Automatic status updates** - Status should change to "in_progress" when technician assigned
4. **Workload management** - Which technician is working on what?

## Proposed Solution

### 1. Add Technician Assignment to Appointment Model

```python
class Appointment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="appointments")
    reported_problem = models.ForeignKey("VehicleProblem", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    
    # 🎯 NEW TECHNICIAN ALLOCATION FIELDS
    assigned_technician = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="assigned_appointments",
        help_text="Technician assigned to work on this appointment"
    )
    assigned_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the technician was assigned"
    )
    started_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When work actually began"
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When work was completed"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled", "Scheduled"),      # ← Changed from "pending"
            ("assigned", "Assigned"),        # ← NEW: Technician assigned but not started
            ("in_progress", "In Progress"),  # ← Work has begun
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
    )
    
    def assign_technician(self, technician):
        """Assign a technician and update status"""
        self.assigned_technician = technician
        self.assigned_at = timezone.now()
        self.status = "assigned"
        self.save()
    
    def start_work(self):
        """Mark work as started"""
        if self.assigned_technician and self.status == "assigned":
            self.started_at = timezone.now()
            self.status = "in_progress"
            self.save()
    
    def complete_work(self):
        """Mark work as completed"""
        if self.status == "in_progress":
            self.completed_at = timezone.now()
            self.status = "completed"
            self.save()
```

### 2. Enhanced Employee Model for Workload Tracking

```python
class Employee(models.Model):
    # ... existing fields ...
    
    # 🎯 WORKLOAD MANAGEMENT PROPERTIES
    @property
    def current_appointments(self):
        """Get appointments currently assigned to this technician"""
        return self.assigned_appointments.filter(
            status__in=["assigned", "in_progress"]
        )
    
    @property
    def workload_count(self):
        """Number of active appointments"""
        return self.current_appointments.count()
    
    @property
    def is_available(self):
        """Check if technician is available for new assignments"""
        return self.workload_count < 3  # Configurable threshold
    
    @property
    def appointments_today(self):
        """Get today's appointments"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.assigned_appointments.filter(date__date=today)
```

## Workflow Implementation

### 1. Appointment Lifecycle Status Flow
```
scheduled → assigned → in_progress → completed
    ↓           ↓           ↓            ↓
Customer    Technician   Work        Work
books       assigned     begins      finished
```

### 2. API Endpoints Needed

```python
# In views.py
@api_view(['POST'])
def assign_technician(request, appointment_id):
    """Assign a technician to an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    technician_id = request.data.get('technician_id')
    technician = get_object_or_404(Employee, id=technician_id)
    
    appointment.assign_technician(technician)
    
    return Response({
        'message': 'Technician assigned successfully',
        'appointment_id': appointment.id,
        'technician': technician.name,
        'status': appointment.status,
        'assigned_at': appointment.assigned_at
    })

@api_view(['POST'])
def start_work(request, appointment_id):
    """Mark appointment work as started"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.start_work()
    
    return Response({
        'message': 'Work started',
        'status': appointment.status,
        'started_at': appointment.started_at
    })
```

### 3. Dashboard Enhancements

```python
# Enhanced shop stats to include technician workload
def shop_stats(request):
    # ... existing stats ...
    
    # 🎯 NEW TECHNICIAN WORKLOAD STATS
    technicians = Employee.objects.filter(role__icontains='technician')
    technician_workload = []
    
    for tech in technicians:
        technician_workload.append({
            'name': tech.name,
            'current_appointments': tech.workload_count,
            'is_available': tech.is_available,
            'appointments_today': tech.appointments_today.count()
        })
    
    return Response({
        # ... existing stats ...
        'technician_workload': technician_workload,
        'available_technicians': [t['name'] for t in technician_workload if t['is_available']]
    })
```

## Benefits of This Enhancement

### ✅ For Shop Management
- **Visual workload tracking** - See which technicians are busy/available
- **Better scheduling** - Assign work to available technicians
- **Performance metrics** - Track completion times per technician

### ✅ For Technicians  
- **Clear work assignments** - See what's assigned to them
- **Status updates** - Mark progress through workflow
- **Workload visibility** - Understand their schedule

### ✅ for Customers
- **Better tracking** - Know when their vehicle is being worked on
- **Realistic estimates** - Based on technician availability
- **Progress updates** - Clear status progression

### ✅ For API Consistency
- **Appointment status flows logically** - scheduled → assigned → in_progress → completed
- **Timestamps track progress** - assigned_at, started_at, completed_at
- **Workload management** - Prevent technician overload

## Migration Strategy

1. **Add new fields** to Appointment model
2. **Update existing appointments** - Set status to "scheduled" 
3. **Create assignment endpoints** for technician allocation
4. **Update frontend** to show technician assignments
5. **Add workload dashboard** for shop management

This enhancement transforms the appointment system from a simple booking system into a comprehensive work allocation and tracking system! 🎯
