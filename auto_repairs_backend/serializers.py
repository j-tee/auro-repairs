from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import for type checking only
    from auto_repairs_backend.models import User as CustomUser

    User = CustomUser
else:
    # Runtime import
    User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.USER_ROLES, default=User.CUSTOMER)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_role(self, value):
        # Only owners can create other owners and employees
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            if value in [User.OWNER, User.EMPLOYEE] and not request.user.is_owner:
                raise serializers.ValidationError(
                    "Only owners can create owner or employee accounts"
                )
        elif value in [User.OWNER, User.EMPLOYEE]:
            # If no authenticated user (public registration), default to customer
            value = User.CUSTOMER
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_active=False,  # User is inactive until email is verified
            email_verification_token=uuid.uuid4(),
            email_verification_sent_at=timezone.now(),
            **validated_data,
        )

        # Send verification email
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email/{user.email_verification_token}"
        )

        subject = "Verify your email address"
        message = f"""
        Hi {user.first_name or user.username},
        
        Please click the link below to verify your email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        Best regards,
        Auto Repairs Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            user = User.objects.get(email_verification_token=value)
            if user.is_verification_token_expired():
                raise serializers.ValidationError("Verification token has expired")
            if user.is_email_verified:
                raise serializers.ValidationError("Email is already verified")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token")


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""

    role_display = serializers.CharField(source="get_role_display", read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "is_email_verified",
            "date_joined",
            "permissions",
        )
        read_only_fields = ("id", "email", "date_joined", "role_display", "permissions")

    def get_permissions(self, obj):
        """Return user permissions based on role"""
        return {
            "can_manage_shops": obj.can_manage_shops,
            "can_manage_employees": obj.can_manage_employees,
            "can_view_all_orders": obj.can_view_all_orders,
            "can_create_repair_orders": obj.can_create_repair_orders,
            "can_manage_inventory": obj.can_manage_inventory,
            "can_view_financial_data": obj.can_view_financial_data,
            "is_owner": obj.is_owner,
            "is_employee": obj.is_employee,
            "is_customer": obj.is_customer,
        }


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (for owners/admins)"""

    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "is_email_verified",
            "is_active",
            "date_joined",
        )
