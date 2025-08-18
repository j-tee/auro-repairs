""" """

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication URLs
    path("api/auth/register/", views.register_user, name="register_user"),
    path("api/auth/verify-email/", views.verify_email, name="verify_email"),
    path(
        "api/auth/resend-verification/",
        views.resend_verification_email,
        name="resend_verification",
    ),
    # JWT Token URLs
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Shop API URLs
    path("api/shop/", include("shop.urls")),
]
