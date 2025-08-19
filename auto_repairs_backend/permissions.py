from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners to access certain views.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_owner


class IsOwnerOrEmployee(permissions.BasePermission):
    """
    Custom permission to allow owners and employees to access certain views.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_owner or request.user.is_employee)
        )


class IsOwnerOrEmployeeOrReadOnlyCustomer(permissions.BasePermission):
    """
    Custom permission to allow:
    - Owners and employees: full access
    - Customers: read-only access to their own data
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # Owners and employees have full access
        if request.user.is_owner or request.user.is_employee:
            return True

        # Customers can only read
        if request.user.is_customer and request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsOwnerOfObject(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for owners
        return request.user and request.user.is_authenticated and request.user.is_owner


class IsCustomerOwnerOfObject(permissions.BasePermission):
    """
    Custom permission for customers to only access their own data.
    """

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        # Owners and employees can access all objects
        if request.user.is_owner or request.user.is_employee:
            return True

        # Customers can only access their own data
        if request.user.is_customer:
            # Check if the object belongs to the customer
            if hasattr(obj, "customer") and hasattr(request.user, "customer_profile"):
                return obj.customer == request.user.customer_profile
            elif hasattr(obj, "user"):
                return obj.user == request.user
            elif obj == request.user:
                return True

        return False


class CanManageShops(permissions.BasePermission):
    """
    Permission for shop management (owners only).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.can_manage_shops
        )


class CanManageEmployees(permissions.BasePermission):
    """
    Permission for employee management (owners only).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.can_manage_employees
        )


class CanViewAllOrders(permissions.BasePermission):
    """
    Permission to view all repair orders (owners and employees).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.can_view_all_orders
        )


class CanCreateRepairOrders(permissions.BasePermission):
    """
    Permission to create repair orders (owners and employees).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.can_create_repair_orders
        )


class CanManageInventory(permissions.BasePermission):
    """
    Permission to manage inventory (owners and employees).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.can_manage_inventory
        )


class CanViewFinancialData(permissions.BasePermission):
    """
    Permission to view financial data (owners only).
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.can_view_financial_data
        )


class RoleBasedPermission(permissions.BasePermission):
    """
    Generic role-based permission class.
    Usage: Add required_roles attribute to your view.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        required_roles = getattr(view, "required_roles", [])
        if not required_roles:
            return True  # No specific roles required

        return request.user.role in required_roles
