from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Shop, Service, Part, Employee, Customer, Appointment, RepairOrder
from auto_repairs_backend.permissions import (
    IsOwner,
    IsOwnerOrEmployee,
    IsCustomerOwnerOfObject,
    CanManageShops,
    CanManageEmployees,
    CanViewAllOrders,
    CanCreateRepairOrders,
    CanManageInventory,
    RoleBasedPermission,
)
from .serializers import (
    ShopSerializer,
    ServiceSerializer,
    PartSerializer,
    EmployeeSerializer,
    CustomerSerializer,
    AppointmentSerializer,
    RepairOrderSerializer,
)


# -------------------
# Protected Test View
# -------------------
class MyProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated"})


# -------------------
# Base ViewSet
# -------------------
class BaseViewSet(viewsets.ModelViewSet):
    """Base viewset with filtering, searching, and ordering."""

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = []  # override in each viewset
    search_fields = []  # override in each viewset
    ordering_fields = []  # override in each viewset
    ordering = ["id"]  # default ordering


# -------------------
# Shop ViewSet
# -------------------
class ShopViewSet(BaseViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, CanManageShops]
    filterset_fields = ["name"]
    search_fields = ["name", "address", "phone"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        """Filter shops based on user role"""
        user = self.request.user
        if user.is_owner:
            return Shop.objects.all()
        elif user.is_employee and hasattr(user, "employee_profile"):
            return Shop.objects.filter(id=user.employee_profile.shop.id)
        return Shop.objects.none()

    @action(detail=True, methods=["get"])
    def employees(self, request, pk=None):
        """Get employees for a specific shop"""
        shop = self.get_object()
        employees = Employee.objects.filter(shop=shop)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def services(self, request, pk=None):
        """Get services for a specific shop"""
        shop = self.get_object()
        services = Service.objects.filter(shop=shop)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


# -------------------
# Service ViewSet
# -------------------
class ServiceViewSet(BaseViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, CanManageInventory]
    filterset_fields = ["shop", "taxable"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "labor_cost"]

    def get_queryset(self):
        """Filter services based on user's accessible shops"""
        user = self.request.user
        accessible_shops = user.get_accessible_shops()
        if accessible_shops:
            return Service.objects.filter(shop__in=accessible_shops)
        return Service.objects.none()


# -------------------
# Part ViewSet
# -------------------
class PartViewSet(BaseViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated, CanManageInventory]
    filterset_fields = ["shop", "category", "taxable"]
    search_fields = ["name", "category", "part_number", "manufacturer"]
    ordering_fields = ["name", "unit_price", "stock_quantity"]

    def get_queryset(self):
        """Filter parts based on user's accessible shops"""
        user = self.request.user
        accessible_shops = user.get_accessible_shops()
        if accessible_shops:
            return Part.objects.filter(shop__in=accessible_shops)
        return Part.objects.none()

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """Get parts with low stock (less than 10 items)"""
        queryset = self.get_queryset().filter(stock_quantity__lt=10)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# -------------------
# Employee ViewSet
# -------------------
class EmployeeViewSet(BaseViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, CanManageEmployees]
    filterset_fields = ["shop", "role"]
    search_fields = ["name", "role", "email"]
    ordering_fields = ["name", "role"]

    def get_queryset(self):
        """Only owners can see all employees"""
        user = self.request.user
        if user.is_owner:
            return Employee.objects.all()
        elif user.is_employee and hasattr(user, "employee_profile"):
            # Employees can only see colleagues in their shop
            return Employee.objects.filter(shop=user.employee_profile.shop)
        return Employee.objects.none()


# -------------------
# Customer ViewSet
# -------------------
class CustomerViewSet(BaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["name", "phone_number", "email"]
    search_fields = ["name", "phone_number", "email", "address"]
    ordering_fields = ["name"]

    def get_queryset(self):
        """Filter customers based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return Customer.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see their own profile
            return Customer.objects.filter(id=user.customer_profile.id)
        return Customer.objects.none()

    def get_permissions(self):
        """Customers can only read their own data"""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsCustomerOwnerOfObject()]
        else:
            return [IsAuthenticated(), IsOwnerOrEmployee()]


# -------------------
# Appointment ViewSet
# -------------------
class AppointmentViewSet(BaseViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["vehicle", "date", "status"]
    search_fields = [
        "vehicle__customer__name",
        "vehicle__make",
        "vehicle__model",
        "status",
    ]
    ordering_fields = ["date", "status"]

    def get_queryset(self):
        """Filter appointments based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return Appointment.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see their own appointments
            return Appointment.objects.filter(vehicle__customer=user.customer_profile)
        return Appointment.objects.none()

    def get_permissions(self):
        """Role-based permissions for appointments"""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated()]  # Anyone can create appointments
        else:
            return [IsAuthenticated(), IsOwnerOrEmployee()]

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming appointments"""
        from django.utils import timezone

        queryset = (
            self.get_queryset()
            .filter(date__gte=timezone.now(), status__in=["pending", "in_progress"])
            .order_by("date")
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# -------------------
# RepairOrder ViewSet
# -------------------
class RepairOrderViewSet(BaseViewSet):
    queryset = RepairOrder.objects.all()
    serializer_class = RepairOrderSerializer
    permission_classes = [IsAuthenticated, CanViewAllOrders]
    filterset_fields = ["vehicle", "date_created"]
    search_fields = [
        "vehicle__customer__name",
        "vehicle__make",
        "vehicle__model",
        "notes",
    ]
    ordering_fields = ["date_created", "total_cost"]

    def get_queryset(self):
        """Filter repair orders based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return RepairOrder.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see their own repair orders
            return RepairOrder.objects.filter(vehicle__customer=user.customer_profile)
        return RepairOrder.objects.none()

    def get_permissions(self):
        """Role-based permissions for repair orders"""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated(), CanCreateRepairOrders()]
        else:
            return [IsAuthenticated(), CanCreateRepairOrders()]

    @action(detail=False, methods=["get"])
    def financial_summary(self, request):
        """Get financial summary (owners only)"""
        if not request.user.can_view_financial_data:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        from django.db.models import Sum, Count

        queryset = self.get_queryset()

        summary = {
            "total_orders": queryset.count(),
            "total_revenue": queryset.aggregate(Sum("total_cost"))["total_cost__sum"]
            or 0,
            "average_order_value": queryset.aggregate(
                avg_cost=Sum("total_cost") / Count("id")
            )["avg_cost"]
            or 0,
        }

        return Response(summary)


# -------------------
# Social Login Views
# # -------------------
# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     serializer_class = JWTSerializer


# class GitHubLogin(SocialLoginView):
#     adapter_class = GitHubOAuth2Adapter
#     serializer_class = JWTSerializer


# class FacebookLogin(SocialLoginView):
#     adapter_class = FacebookOAuth2Adapter
#     serializer_class = JWTSerializer

# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }
