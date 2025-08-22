from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register all ViewSets
router = DefaultRouter()
router.register(r"vehicles", views.VehicleViewSet)
router.register(r"customers", views.CustomerViewSet)
router.register(r"employees", views.EmployeeViewSet)
router.register(r"shops", views.ShopViewSet)
router.register(r"services", views.ServiceViewSet)
router.register(r"parts", views.PartViewSet)
router.register(r"vehicle-problems", views.VehicleProblemViewSet)
router.register(r"appointments", views.AppointmentViewSet)
router.register(r"repair-orders", views.RepairOrderViewSet)
router.register(r"repair-order-services", views.RepairOrderServiceViewSet)
router.register(r"repair-order-parts", views.RepairOrderPartViewSet)

urlpatterns = [
    # Global search endpoint
    path("search/", views.global_search, name="global_search"),
    # Nested resource endpoints for better API organization
    path(
        "customers/<int:customer_id>/vehicles/",
        views.VehicleViewSet.as_view({"get": "by_customer"}),
        name="customer_vehicles",
    ),
    path(
        "customers/<int:customer_id>/appointments/",
        views.AppointmentViewSet.as_view({"get": "list"}),
        name="customer_appointments",
    ),
    path(
        "customers/<int:customer_id>/repair-orders/",
        views.RepairOrderViewSet.as_view({"get": "by_customer"}),
        name="customer_repair_orders",
    ),
    path(
        "vehicles/<int:vehicle_id>/problems/",
        views.VehicleProblemViewSet.as_view({"get": "by_vehicle"}),
        name="vehicle_problems",
    ),
    path(
        "vehicles/<int:vehicle_id>/appointments/",
        views.AppointmentViewSet.as_view({"get": "list"}),
        name="vehicle_appointments",
    ),
    path(
        "vehicles/<int:vehicle_id>/repair-orders/",
        views.RepairOrderViewSet.as_view({"get": "by_vehicle"}),
        name="vehicle_repair_orders",
    ),
    # Include all router URLs
    path("", include(router.urls)),
]
