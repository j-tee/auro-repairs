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
@permission_classes([IsAuthenticated])
def get_employee_profile(request):
    """
    Get Employee record linked to the authenticated User for technician dashboard
    Maps authenticated User ID to Employee ID for filtering appointments
    """
    from shop.models import Employee
    from shop.serializers import EmployeeSerializer
    
    try:
        # Find employee record linked to the authenticated user
        employee = Employee.objects.select_related('shop').get(user=request.user)
        
        response_data = {
            "user_id": request.user.id,
            "employee": {
                "id": employee.id,
                "name": employee.name,
                "role": employee.role,
                "email": employee.email,
                "phone": employee.phone_number,
                "shop": {
                    "id": employee.shop.id,
                    "name": employee.shop.name
                } if employee.shop else None
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Employee.DoesNotExist:
        return Response(
            {
                "error": "No employee record found for this user",
                "detail": "This user account is not linked to an employee record. Contact your administrator."
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customer_profile(request):
    """
    Get Customer record linked to the authenticated User for customer dashboard
    Maps authenticated User ID to Customer ID and provides customer information
    """
    from shop.models import Customer
    
    try:
        # Find customer record linked to the authenticated user
        customer = Customer.objects.get(user=request.user)
        
        response_data = {
            "user_id": request.user.id,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone_number,
                "address": customer.address
            },
            "user_role": request.user.role
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Customer.DoesNotExist:
        return Response(
            {
                "error": "No customer record found for this user",
                "detail": "This user account is not linked to a customer record. Please contact support."
            },
            status=status.HTTP_404_NOT_FOUND
        )


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


@api_view(["GET"])
@permission_classes([IsOwner])
def get_user_stats(request):
    """
    Get comprehensive user statistics (only accessible by owners)
    Returns user count totals, role distribution, verification rates, and recent activity
    """
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    # Get total user count
    total_users = User.objects.count()
    
    # Get role distribution
    role_stats = {
        "owners": User.objects.filter(role=User.OWNER).count(),
        "employees": User.objects.filter(role=User.EMPLOYEE).count(),
        "customers": User.objects.filter(role=User.CUSTOMER).count(),
    }
    
    # Get email verification stats
    verified_users = User.objects.filter(is_email_verified=True).count()
    unverified_users = total_users - verified_users
    verification_rate = (verified_users / total_users * 100) if total_users > 0 else 0
    
    # Get active user stats (users who have logged in recently)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users = User.objects.filter(last_login__gte=thirty_days_ago).count()
    
    # Get recent registrations (last 30 days)
    recent_registrations = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Calculate percentages for role distribution
    role_percentages = {}
    if total_users > 0:
        role_percentages = {
            "owners": (role_stats["owners"] / total_users * 100),
            "employees": (role_stats["employees"] / total_users * 100),
            "customers": (role_stats["customers"] / total_users * 100),
        }
    
    stats_data = {
        "total_users": total_users,
        "role_distribution": {
            "counts": role_stats,
            "percentages": role_percentages,
        },
        "email_verification": {
            "verified_count": verified_users,
            "unverified_count": unverified_users,
            "verification_rate": round(verification_rate, 2),
        },
        "activity": {
            "active_users_30_days": active_users,
            "recent_registrations_30_days": recent_registrations,
        },
        "summary": {
            "active_rate": round((active_users / total_users * 100), 2) if total_users > 0 else 0,
            "growth_rate": round((recent_registrations / total_users * 100), 2) if total_users > 0 else 0,
        }
    }
    
    return Response(stats_data, status=status.HTTP_200_OK)
