from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    # User roles
    OWNER = "owner"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"

    USER_ROLES = [
        (OWNER, "Owner"),
        (EMPLOYEE, "Employee"),
        (CUSTOMER, "Customer"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default=CUSTOMER,
        help_text="User role determines access privileges",
    )
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True
    )
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"  # type: ignore

    def is_verification_token_expired(self):
        if not self.email_verification_sent_at:
            return True
        expiry_time = self.email_verification_sent_at + timedelta(hours=24)
        return timezone.now() > expiry_time

    @property
    def is_owner(self):
        """Check if user is an owner"""
        return self.role == self.OWNER

    @property
    def is_employee(self):
        """Check if user is an employee"""
        return self.role == self.EMPLOYEE

    @property
    def is_customer(self):
        """Check if user is a customer"""
        return self.role == self.CUSTOMER

    @property
    def can_manage_shops(self):
        """Owners can manage shops"""
        return self.is_owner

    @property
    def can_manage_employees(self):
        """Owners can manage employees"""
        return self.is_owner

    @property
    def can_view_all_orders(self):
        """Owners and employees can view all repair orders"""
        return self.is_owner or self.is_employee

    @property
    def can_create_repair_orders(self):
        """Owners and employees can create repair orders"""
        return self.is_owner or self.is_employee

    @property
    def can_manage_inventory(self):
        """Owners and employees can manage parts and services"""
        return self.is_owner or self.is_employee

    @property
    def can_view_financial_data(self):
        """Only owners can view financial data"""
        return self.is_owner

    def get_accessible_shops(self):
        """Get shops this user can access"""
        if self.is_owner:
            from shop.models import Shop

            return Shop.objects.all()
        elif self.is_employee and hasattr(self, "employee_profile"):  # type: ignore
            return [self.employee_profile.shop]  # type: ignore
        return []
