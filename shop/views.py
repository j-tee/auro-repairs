from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Shop, Service, Part, Employee, Customer, Appointment, RepairOrder
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    ShopSerializer, ServiceSerializer, PartSerializer,
    EmployeeSerializer, CustomerSerializer, AppointmentSerializer,
    RepairOrderSerializer
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []   # override in each viewset
    search_fields = []      # override in each viewset
    ordering_fields = []    # override in each viewset
    ordering = ['id']       # default ordering


# -------------------
# Shop ViewSet
# -------------------
class ShopViewSet(BaseViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    filterset_fields = ['owner', 'name', 'subscription_plan']
    search_fields = ['name', 'owner__username']
    ordering_fields = ['name', 'subscription_plan']


# -------------------
# Service ViewSet
# -------------------
class ServiceViewSet(BaseViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filterset_fields = ['shop', 'name', 'taxable']
    search_fields = ['name', 'shop__name']
    ordering_fields = ['name', 'labor_cost']


# -------------------
# Part ViewSet
# -------------------
class PartViewSet(BaseViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    filterset_fields = ['shop', 'category', 'taxable']
    search_fields = ['name', 'category', 'part_number']
    ordering_fields = ['name', 'unit_price', 'stock_quantity']


# -------------------
# Employee ViewSet
# -------------------
class EmployeeViewSet(BaseViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filterset_fields = ['shop', 'role']
    search_fields = ['name', 'role', 'shop__name']
    ordering_fields = ['name', 'role']


# -------------------
# Customer ViewSet
# -------------------
class CustomerViewSet(BaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ['name', 'phone_number', 'email']
    search_fields = ['name', 'phone_number', 'email']
    ordering_fields = ['name']

# -------------------
# Appointment ViewSet
# -------------------
class AppointmentViewSet(BaseViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filterset_fields = ['vehicle', 'service', 'date', 'status']
    search_fields = ['vehicle__customer__name', 'vehicle__vin', 'service__name', 'status']
    ordering_fields = ['date', 'status']


# -------------------
# RepairOrder ViewSet
# -------------------
class RepairOrderViewSet(BaseViewSet):
    queryset = RepairOrder.objects.all()
    serializer_class = RepairOrderSerializer
    filterset_fields = ['vehicle', 'services', 'date_created']
    search_fields = ['vehicle__customer__name', 'services__shop__name']
    ordering_fields = ['date_created', 'total_cost']


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