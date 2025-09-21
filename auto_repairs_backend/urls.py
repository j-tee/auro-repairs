""" """

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication URLs
    path("api/auth/register/", views.register_user, name="register_user"),
    path("api/auth/user/", views.get_user_profile, name="get_user_profile"),
    path("api/auth/employee-profile/", views.get_employee_profile, name="get_employee_profile"),
    path("api/auth/customer-profile/", views.get_customer_profile, name="get_customer_profile"),
    path(
        "api/auth/user/update/", views.update_user_profile, name="update_user_profile"
    ),
    path("api/auth/verify-email/", views.verify_email, name="verify_email"),
    path(
        "api/auth/resend-verification/",
        views.resend_verification_email,
        name="resend_verification",
    ),
    # Admin-only endpoints (require owner permission)
    path("api/admin/users/", views.list_users, name="admin-list-users"),
    path("api/admin/users/stats/", views.get_user_stats, name="admin-user-stats"),
    path(
        "api/admin/users/<int:user_id>/role/",
        views.update_user_role,
        name="admin-update-user-role",
    ),
    # JWT Token URLs
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Shop API URLs
    path("api/shop/", include("shop.urls")),
]
