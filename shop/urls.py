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
router.register(r"repair-orders", views.RepairOrderViewSet)
router.register(r"repair-order-services", views.RepairOrderServiceViewSet)
router.register(r"repair-order-parts", views.RepairOrderPartViewSet)

urlpatterns = [
    # Global search endpoint
    path("search/", views.global_search, name="global_search"),
    # Include all router URLs
    path("", include(router.urls)),
]
