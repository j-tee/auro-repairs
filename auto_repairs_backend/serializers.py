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

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
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
