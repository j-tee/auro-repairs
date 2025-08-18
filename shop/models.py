from django.db import models
from django.conf import settings
from decimal import Decimal

# Create your models here.
from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Shop"
        verbose_name_plural = "Shops"
        ordering = ['-created_at']



# -------------------
# Employees
# -------------------
class Employee(models.Model):
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="employees")
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)  # mechanic, receptionist, etc.
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    picture = models.ImageField(
        upload_to='employee_pics/', blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        blank=True,
        null=True
    )

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
        null=True
    )

    def __str__(self):
        return self.name


# -------------------
# Vehicles
# -------------------
class Vehicle(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="vehicles")
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
        Vehicle, on_delete=models.CASCADE, related_name="problems")
    description = models.TextField()
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vehicle} - {self.description[:50]}"



# -------------------
# Services
# -------------------
class Service(models.Model):
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="services")
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
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="parts")
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
        'VehicleProblem', on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments"
    )
    description = models.TextField(blank=True, null=True)  # Optional notes by customer
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending"
    )

    def __str__(self):
        problem = self.reported_problem.description[:50] if self.reported_problem else "No problem reported"
        return f"{self.vehicle.customer.name} - {self.vehicle} - {problem}"

# -------------------
# Repair Orders
# -------------------
class RepairOrder(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="repair_orders")
    services = models.ManyToManyField(Service, through="RepairOrderService")
    parts = models.ManyToManyField(
        Part, through="RepairOrderPart", related_name="repair_orders")
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"))
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"))
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"))
    date_created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def calculate_total_cost(self):
        labor_total = sum(s.labor_cost for s in self.services.all())
        parts_total = sum(
            item.part.unit_price * item.quantity for item in self.repair_order_parts.all() # type: ignore[attr-defined]
            )
        subtotal = labor_total + parts_total

        discount_value = Decimal("0.00")
        if self.discount_percent > 0:
            discount_value = (
                subtotal * self.discount_percent) / Decimal("100")
        elif self.discount_amount > 0:
            discount_value = self.discount_amount

        taxable_services_total = sum(
            s.labor_cost for s in self.services.all() if s.taxable)
        taxable_parts_total = sum(
            item.part.unit_price * item.quantity for item in self.repair_order_parts.all() if item.part.taxable # type: ignore[attr-defined]
            )
        taxable_amount = (taxable_services_total +
                          taxable_parts_total) - discount_value
        tax_value = (taxable_amount * self.tax_percent) / \
            Decimal("100") if self.tax_percent > 0 else Decimal("0.00")

        return subtotal - discount_value + tax_value

    def save(self, *args, **kwargs):
        self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Repair Order #{self.pk} - {self.vehicle}"


class RepairOrderPart(models.Model):
    repair_order = models.ForeignKey(
        RepairOrder, on_delete=models.CASCADE, related_name="repair_order_parts")
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    warranty_override_months = models.PositiveIntegerField(
        null=True, blank=True)

    @property
    def total_price(self):
        return self.part.unit_price * self.quantity

class RepairOrderService(models.Model):
    repair_order = models.ForeignKey(
        RepairOrder, on_delete=models.CASCADE, related_name="repair_order_services")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    warranty_override_months = models.PositiveIntegerField(
        null=True, blank=True)
