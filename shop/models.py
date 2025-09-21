from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# Create your models here.
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    bay_count = models.PositiveIntegerField(
        default=4, help_text="Number of service bays"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether shop is operational"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"
        ordering = ["-created_at"]


# -------------------
# Employees
# -------------------
class Employee(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="employees")
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)  # mechanic, receptionist, etc.
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    picture = models.ImageField(upload_to="employee_pics/", blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        blank=True,
        null=True,
    )

    # 🎯 WORKLOAD MANAGEMENT PROPERTIES
    @property
    def current_appointments(self):
        """Get appointments currently assigned to this technician"""
        return self.assigned_appointments.filter(
            status__in=["assigned", "in_progress"]
        )

    @property
    def workload_count(self):
        """Number of active appointments assigned to this technician"""
        return self.current_appointments.count()

    @property
    def is_available(self):
        """Check if technician is available for new assignments"""
        # Configurable threshold - technicians can handle max 3 concurrent jobs
        return self.workload_count < 3

    @property
    def appointments_today(self):
        """Get today's appointments for this technician"""
        today = timezone.now().date()
        return self.assigned_appointments.filter(date__date=today)

    @property
    def current_jobs(self):
        """Get current job assignments with detailed information for frontend"""
        appointments = self.current_appointments
        jobs = []
        
        for appointment in appointments:
            # Get customer through vehicle relationship
            customer_name = appointment.vehicle.customer.name if appointment.vehicle and appointment.vehicle.customer else 'Unknown Customer'
            vehicle_info = f"{appointment.vehicle.make} {appointment.vehicle.model}" if appointment.vehicle else 'Unknown Vehicle'
            
            job_data = {
                'appointment_id': appointment.id,
                'customer_name': customer_name,
                'vehicle': vehicle_info,
                'service_type': 'General Repair',  # Will be enhanced when service relationship is added
                'status': appointment.status,
                'started_at': appointment.date,
                'estimated_completion': None  # Could be calculated based on service duration
            }
            jobs.append(job_data)
        
        return jobs

    @property
    def is_technician(self):
        """Check if this employee is a technician"""
        return "technician" in self.role.lower() or "mechanic" in self.role.lower()

    def __str__(self):
        return f"{self.name} - {self.shop.name}"


# -------------------
# Customers
# -------------------
class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


# -------------------
# Vehicles
# -------------------
class Vehicle(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="vehicles"
    )
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    vin = models.CharField(max_length=100, unique=True)
    license_plate = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate or self.vin})"


# -------------------
# Vehicle Problems
# -------------------
class VehicleProblem(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="problems"
    )
    description = models.TextField()
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vehicle} - {self.description[:50]}"


# -------------------
# Services
# -------------------
class Service(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    taxable = models.BooleanField(default=True)
    warranty_months = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.shop.name}"


# -------------------
# Parts
# -------------------
class Part(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="parts")
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # used, new, refurbished
    part_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    taxable = models.BooleanField(default=True)
    warranty_months = models.PositiveIntegerField(default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        return self.unit_price * self.stock_quantity

    def __str__(self):
        return f"{self.name} - {self.shop.name}"


# -------------------
# Appointments
# -------------------
class Appointment(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="appointments"
    )
    reported_problem = models.ForeignKey(
        "VehicleProblem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    description = models.TextField(blank=True, null=True)  # Optional notes by customer
    date = models.DateTimeField()
    
    # 🎯 TECHNICIAN ALLOCATION FIELDS
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
            ("pending", "Pending"),          # Customer booked appointment (initial status)
            ("assigned", "Assigned"),        # Technician assigned but not started
            ("in_progress", "In Progress"),  # Work has begun
            ("completed", "Completed"),      # Work finished
            ("cancelled", "Cancelled"),      # Appointment cancelled
        ],
        default="pending",
    )

    def assign_technician(self, technician):
        """Assign a technician and update status to assigned"""
        self.assigned_technician = technician
        self.assigned_at = timezone.now()
        if self.status == "pending":
            self.status = "assigned"
        self.save()
        return self

    def start_work(self):
        """Mark work as started - status becomes in_progress"""
        if self.assigned_technician and self.status == "assigned":
            self.started_at = timezone.now()
            self.status = "in_progress"
            self.save()
        return self

    def complete_work(self):
        """Mark work as completed"""
        if self.status == "in_progress":
            self.completed_at = timezone.now()
            self.status = "completed"
            self.save()
        return self

    def __str__(self):
        problem = (
            self.reported_problem.description[:50]
            if self.reported_problem
            else "No problem reported"
        )
        tech_info = f" [Tech: {self.assigned_technician.name}]" if self.assigned_technician else ""
        return f"{self.vehicle.customer.name} - {self.vehicle} - {problem}{tech_info}"


# -------------------
# Repair Orders
# -------------------
class RepairOrder(models.Model):
    # EXISTING DATABASE FIELDS (DO NOT CHANGE)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="repair_orders"
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("8.25")
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    date_created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    # Many-to-many relationships through intermediate models
    services = models.ManyToManyField(Service, through="RepairOrderService")
    parts = models.ManyToManyField(
        Part, through="RepairOrderPart", related_name="repair_orders"
    )

    # COMPUTED PROPERTIES (no database fields)
    @property
    def customer(self):
        """Get customer through vehicle relationship"""
        return self.vehicle.customer

    @property
    def is_completed(self):
        """Check if any related appointments are completed"""
        return self.vehicle.appointments.filter(status="completed").exists()  # type: ignore

    @property
    def related_appointments(self):
        """Get all appointments for the same vehicle"""
        return self.vehicle.appointments.all()  # type: ignore

    def calculate_total_cost(self):
        # Calculate labor costs from services through RepairOrderService
        labor_total = sum(
            ros.service.labor_cost for ros in self.repair_order_services.all()  # type: ignore
        )

        # Calculate parts costs from parts through RepairOrderPart
        parts_total = sum(
            item.part.unit_price * item.quantity
            for item in self.repair_order_parts.all()  # type: ignore
        )

        subtotal = labor_total + parts_total

        # Calculate discount
        discount_value = self.discount_amount
        if self.discount_percent > 0:
            discount_value += (subtotal * self.discount_percent) / Decimal("100")

        # Calculate tax on taxable items
        taxable_services_total = sum(
            ros.service.labor_cost
            for ros in self.repair_order_services.all()  # type: ignore
            if ros.service.taxable
        )
        taxable_parts_total = sum(
            item.part.unit_price * item.quantity
            for item in self.repair_order_parts.all()  # type: ignore
            if item.part.taxable
        )
        taxable_amount = (taxable_services_total + taxable_parts_total) - discount_value
        tax_value = (
            (taxable_amount * self.tax_percent) / Decimal("100")
            if self.tax_percent > 0
            else Decimal("0.00")
        )

        return subtotal - discount_value + tax_value

    def save(self, *args, **kwargs):
        # Only calculate total cost if the object already exists (has an ID)
        skip_calculation = kwargs.pop("skip_calculation", False)
        if not skip_calculation and self.pk is not None:
            self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Repair Order #{self.pk} - {self.vehicle}"


class RepairOrderPart(models.Model):
    repair_order = models.ForeignKey(
        RepairOrder, on_delete=models.CASCADE, related_name="repair_order_parts"
    )
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    warranty_override_months = models.PositiveIntegerField(null=True, blank=True)

    @property
    def total_price(self):
        return self.part.unit_price * self.quantity


class RepairOrderService(models.Model):
    repair_order = models.ForeignKey(
        RepairOrder, on_delete=models.CASCADE, related_name="repair_order_services"
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    warranty_override_months = models.PositiveIntegerField(null=True, blank=True)
