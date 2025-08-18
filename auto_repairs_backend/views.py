from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, EmailVerificationSerializer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_repairs_backend.models import User as CustomUser

    User = CustomUser
else:
    User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and send email verification
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Handle if serializer.save() returns a list of users
        if isinstance(user, list):
            user_obj = user[0] if user else None
        else:
            user_obj = user

        if user_obj is not None:
            return Response(
                {
                    "message": "User registered successfully. Please check your email to verify your account.",
                    "user_id": str(user_obj.id),
                    "email": str(user_obj.email),
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "User registration failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user email with token
    """
    serializer = EmailVerificationSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data if serializer.validated_data else {}
        token = validated_data.get("token")
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True
            user.is_active = True  # Activate the user
            user.email_verification_token = None  # Clear the token
            user.email_verification_sent_at = None
            user.save()

            return Response(
                {"message": "Email verified successfully. You can now log in."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend verification email to user
    """
    email = request.data.get("email")
    if not email:
        return Response(
            {"error": "Email field is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if user.is_email_verified:
            return Response(
                {"message": "Email is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update verification token and timestamp
        import uuid
        from django.utils import timezone

        user.email_verification_token = uuid.uuid4()
        user.email_verification_sent_at = timezone.now()
        user.save()

        # Send verification email using the serializer method
        serializer_instance = UserRegistrationSerializer()
        serializer_instance.send_verification_email(user)

        return Response(
            {"message": "Verification email sent successfully"},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"error": "User with this email does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )
