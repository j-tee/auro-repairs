from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    EmailVerificationSerializer,
    UserProfileSerializer,
    UserListSerializer,
)
from .permissions import IsOwner, IsOwnerOrEmployee
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
    serializer = UserRegistrationSerializer(
        data=request.data, context={"request": request}
    )
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
                    "role": user_obj.role,  # type: ignore
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
        validated_data = getattr(serializer, 'validated_data', {})  # type: ignore
        token = validated_data.get("token")  # type: ignore
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True  # type: ignore
            user.is_active = True  # Activate the user
            user.email_verification_token = None  # type: ignore - Clear the token
            user.email_verification_sent_at = None  # type: ignore
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
        if user.is_email_verified:  # type: ignore
            return Response(
                {"message": "Email is already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update verification token and timestamp
        import uuid
        from django.utils import timezone

        user.email_verification_token = uuid.uuid4()  # type: ignore
        user.email_verification_sent_at = timezone.now()  # type: ignore
        user.save()

        # Send verification email using the serializer method
        serializer_instance = UserRegistrationSerializer()
        serializer_instance.send_verification_email(user)  # type: ignore

        return Response(
            {"message": "Verification email sent successfully"},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"error": "User with this email does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current authenticated user profile with role-based permissions
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsOwner])
def list_users(request):
    """
    List all users (only accessible by owners)
    """
    users = User.objects.all().order_by("-date_joined")
    serializer = UserListSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update current user profile
    """
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsOwner])
def update_user_role(request, user_id):
    """
    Update user role (only accessible by owners)
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    new_role = request.data.get("role")
    if new_role not in [choice[0] for choice in User.USER_ROLES]:  # type: ignore
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    user.role = new_role  # type: ignore
    user.save()

    serializer = UserProfileSerializer(user)
    return Response(
        {
            "message": f"User role updated to {user.get_role_display()}",  # type: ignore
            "user": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
