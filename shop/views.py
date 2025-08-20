from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    Shop,
    Service,
    Part,
    Employee,
    Customer,
    Vehicle,
    VehicleProblem,
    Appointment,
    RepairOrder,
    RepairOrderPart,
    RepairOrderService,
)
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
    VehicleSerializer,
    VehicleProblemSerializer,
    AppointmentSerializer,
    RepairOrderSerializer,
    RepairOrderPartSerializer,
    RepairOrderServiceSerializer,
)


# -------------------
# Protected Test View
# -------------------
class MyProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated"})


# -------------------
# Global Search API
# -------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def global_search(request):
    """
    Global search across vehicles, customers, and repair orders.
    Query parameter: ?q=search_term
    """
    search_query = request.GET.get("q", "").strip()

    if not search_query:
        return Response(
            {"vehicles": [], "customers": [], "repair_orders": [], "total_results": 0}
        )

    # Get user for role-based filtering
    user = request.user

    # Initialize results
    results = {"vehicles": [], "customers": [], "repair_orders": [], "total_results": 0}

    try:
        # Search Vehicles - ONLY by vehicle attributes, not customer names
        vehicle_queryset = Vehicle.objects.none()
        if user.is_owner or user.is_employee:
            vehicle_queryset = Vehicle.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            vehicle_queryset = Vehicle.objects.filter(customer=user.customer_profile)

        vehicles = vehicle_queryset.filter(
            Q(make__icontains=search_query)
            | Q(model__icontains=search_query)
            | Q(vin__icontains=search_query)
            | Q(license_plate__icontains=search_query)
            | Q(color__icontains=search_query)
        ).select_related("customer")

        # Serialize vehicles
        vehicle_results = []
        for vehicle in vehicles:
            vehicle_results.append(
                {
                    "id": vehicle.id,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "year": vehicle.year,
                    "vin": vehicle.vin,
                    "license_plate": vehicle.license_plate,
                    "color": vehicle.color,
                    "customer_name": (
                        vehicle.customer.name
                        if vehicle.customer
                        else "Unknown Customer"
                    ),
                    "customer_email": (
                        vehicle.customer.email if vehicle.customer else None
                    ),
                    "type": "vehicle",
                }
            )
        results["vehicles"] = vehicle_results

        # Search Customers - by customer attributes AND customers who own matching vehicles
        customer_queryset = Customer.objects.none()
        if user.is_owner or user.is_employee:
            customer_queryset = Customer.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            customer_queryset = Customer.objects.filter(id=user.customer_profile.id)

        customers = customer_queryset.filter(
            Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(address__icontains=search_query)
            | Q(phone_number__icontains=search_query)
            | Q(vehicles__make__icontains=search_query)
            | Q(vehicles__model__icontains=search_query)
        ).distinct()

        # Serialize customers
        customer_results = []
        for customer in customers:
            customer_results.append(
                {
                    "id": customer.id,
                    "name": customer.name,
                    "email": customer.email,
                    "phone_number": customer.phone_number,
                    "address": customer.address,
                    "type": "customer",
                }
            )
        results["customers"] = customer_results

        # Search Repair Orders - by notes AND orders for matching vehicles
        order_queryset = RepairOrder.objects.none()
        if user.is_owner or user.is_employee:
            order_queryset = RepairOrder.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            order_queryset = RepairOrder.objects.filter(
                vehicle__customer=user.customer_profile
            )

        repair_orders = order_queryset.filter(
            Q(notes__icontains=search_query)
            | Q(vehicle__make__icontains=search_query)
            | Q(vehicle__model__icontains=search_query)
            | Q(vehicle__vin__icontains=search_query)
        ).select_related("vehicle", "vehicle__customer")

        # Serialize repair orders
        order_results = []
        for order in repair_orders:
            order_results.append(
                {
                    "id": order.id,
                    "total_cost": float(order.total_cost),
                    "date_created": order.date_created.isoformat(),
                    "notes": order.notes,
                    "vehicle": (
                        {
                            "id": order.vehicle.id,
                            "make": order.vehicle.make,
                            "model": order.vehicle.model,
                            "year": order.vehicle.year,
                            "customer_name": (
                                order.vehicle.customer.name
                                if order.vehicle.customer
                                else "Unknown Customer"
                            ),
                        }
                        if order.vehicle
                        else None
                    ),
                    "type": "repair_order",
                }
            )
        results["repair_orders"] = order_results

        # Calculate total results
        results["total_results"] = (
            len(vehicle_results) + len(customer_results) + len(order_results)
        )

        return Response(results)

    except Exception as e:
        return Response(
            {"error": f"Search failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
# Vehicle ViewSet
# -------------------
class VehicleViewSet(BaseViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["customer", "make", "model", "year"]
    search_fields = ["make", "model", "vin", "license_plate", "color"]
    ordering_fields = ["make", "model", "year"]

    def get_queryset(self):
        """Filter vehicles based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return Vehicle.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see their own vehicles
            return Vehicle.objects.filter(customer=user.customer_profile)
        return Vehicle.objects.none()

    def get_permissions(self):
        """Role-based permissions for vehicles"""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated()]  # Anyone can create vehicles
        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsCustomerOwnerOfObject()]
        else:
            return [IsAuthenticated(), IsOwnerOrEmployee()]


# -------------------
# Vehicle Problem ViewSet
# -------------------
class VehicleProblemViewSet(BaseViewSet):
    queryset = VehicleProblem.objects.all()
    serializer_class = VehicleProblemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["vehicle", "resolved"]
    search_fields = [
        "description",
        "vehicle__make",
        "vehicle__model",
        "vehicle__customer__name",
    ]
    ordering_fields = ["reported_date", "resolved"]

    def get_queryset(self):
        """Filter vehicle problems based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return VehicleProblem.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see problems for their own vehicles
            return VehicleProblem.objects.filter(
                vehicle__customer=user.customer_profile
            )
        return VehicleProblem.objects.none()

    def get_permissions(self):
        """Role-based permissions for vehicle problems"""
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated()]  # Anyone can report problems
        elif self.action in ["update", "partial_update"]:
            # Only customers can update their own problems, or employees/owners
            return [IsAuthenticated(), IsCustomerOwnerOfObject()]
        else:
            return [IsAuthenticated(), IsOwnerOrEmployee()]

    @action(detail=False, methods=["get"])
    def unresolved(self, request):
        """Get unresolved vehicle problems"""
        queryset = self.get_queryset().filter(resolved=False).order_by("reported_date")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


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
# RepairOrderPart ViewSet
# -------------------
class RepairOrderPartViewSet(BaseViewSet):
    queryset = RepairOrderPart.objects.all()
    serializer_class = RepairOrderPartSerializer
    permission_classes = [IsAuthenticated, CanCreateRepairOrders]
    filterset_fields = ["repair_order", "part"]
    search_fields = ["part__name", "part__part_number", "repair_order__id"]
    ordering_fields = ["quantity", "part__name"]

    def get_queryset(self):
        """Filter repair order parts based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return RepairOrderPart.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see parts for their own repair orders
            return RepairOrderPart.objects.filter(
                repair_order__vehicle__customer=user.customer_profile
            )
        return RepairOrderPart.objects.none()


# -------------------
# RepairOrderService ViewSet
# -------------------
class RepairOrderServiceViewSet(BaseViewSet):
    queryset = RepairOrderService.objects.all()
    serializer_class = RepairOrderServiceSerializer
    permission_classes = [IsAuthenticated, CanCreateRepairOrders]
    filterset_fields = ["repair_order", "service"]
    search_fields = ["service__name", "repair_order__id"]
    ordering_fields = ["service__name", "service__labor_cost"]

    def get_queryset(self):
        """Filter repair order services based on user role"""
        user = self.request.user
        if user.is_owner or user.is_employee:
            return RepairOrderService.objects.all()
        elif user.is_customer and hasattr(user, "customer_profile"):
            # Customers can only see services for their own repair orders
            return RepairOrderService.objects.filter(
                repair_order__vehicle__customer=user.customer_profile
            )
        return RepairOrderService.objects.none()


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
