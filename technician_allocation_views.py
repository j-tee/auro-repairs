"""
TECHNICIAN ALLOCATION API ENDPOINTS
Add these functions to shop/views.py to enable technician assignment functionality
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Appointment, Employee
from .serializers import AppointmentSerializer, EmployeeSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_technician(request, appointment_id):
    """
    Assign a technician to an appointment
    
    POST /api/shop/appointments/{id}/assign-technician/
    Body: {"technician_id": 5}
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    technician_id = request.data.get('technician_id')
    
    if not technician_id:
        return Response(
            {'error': 'technician_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    technician = get_object_or_404(Employee, id=technician_id)
    
    # Check if technician is available
    if not technician.is_available:
        return Response({
            'error': f'Technician {technician.name} is not available',
            'current_workload': technician.workload_count,
            'max_workload': 3
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Assign the technician
    appointment.assign_technician(technician)
    
    # Return updated appointment data
    serializer = AppointmentSerializer(appointment)
    
    return Response({
        'message': 'Technician assigned successfully',
        'appointment': serializer.data,
        'technician': {
            'id': technician.id,
            'name': technician.name,
            'role': technician.role
        },
        'assignment_details': {
            'assigned_at': appointment.assigned_at,
            'status': appointment.status,
            'previous_status': 'scheduled'
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_work(request, appointment_id):
    """
    Mark appointment work as started (status: assigned → in_progress)
    
    POST /api/shop/appointments/{id}/start-work/
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not appointment.assigned_technician:
        return Response({
            'error': 'No technician assigned to this appointment'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if appointment.status != 'assigned':
        return Response({
            'error': f'Cannot start work. Current status: {appointment.status}',
            'valid_status_for_start': 'assigned'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Start the work
    previous_status = appointment.status
    appointment.start_work()
    
    serializer = AppointmentSerializer(appointment)
    
    return Response({
        'message': 'Work started successfully',
        'appointment': serializer.data,
        'work_details': {
            'started_at': appointment.started_at,
            'status': appointment.status,
            'previous_status': previous_status,
            'technician': appointment.assigned_technician.name
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_work(request, appointment_id):
    """
    Mark appointment work as completed (status: in_progress → completed)
    
    POST /api/shop/appointments/{id}/complete-work/
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'in_progress':
        return Response({
            'error': f'Cannot complete work. Current status: {appointment.status}',
            'valid_status_for_completion': 'in_progress'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Complete the work
    previous_status = appointment.status
    appointment.complete_work()
    
    serializer = AppointmentSerializer(appointment)
    
    return Response({
        'message': 'Work completed successfully',
        'appointment': serializer.data,
        'completion_details': {
            'completed_at': appointment.completed_at,
            'status': appointment.status,
            'previous_status': previous_status,
            'technician': appointment.assigned_technician.name,
            'total_work_time': str(appointment.completed_at - appointment.started_at) if appointment.started_at else None
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def technician_workload(request):
    """
    Get workload information for all technicians
    
    GET /api/shop/technicians/workload/
    """
    technicians = Employee.objects.filter(
        role__icontains='technician'
    ).select_related('shop')
    
    workload_data = []
    
    for tech in technicians:
        current_appointments = tech.current_appointments
        today_appointments = tech.appointments_today
        
        workload_data.append({
            'technician': {
                'id': tech.id,
                'name': tech.name,
                'role': tech.role,
                'shop': tech.shop.name
            },
            'workload': {
                'current_appointments': tech.workload_count,
                'is_available': tech.is_available,
                'appointments_today': today_appointments.count(),
                'max_capacity': 3
            },
            'current_jobs': [
                {
                    'appointment_id': apt.id,
                    'vehicle': f"{apt.vehicle.make} {apt.vehicle.model}",
                    'customer': apt.vehicle.customer.name,
                    'status': apt.status,
                    'assigned_at': apt.assigned_at,
                    'started_at': apt.started_at
                } for apt in current_appointments
            ]
        })
    
    # Summary statistics
    total_technicians = len(workload_data)
    available_technicians = len([t for t in workload_data if t['workload']['is_available']])
    busy_technicians = total_technicians - available_technicians
    
    return Response({
        'summary': {
            'total_technicians': total_technicians,
            'available_technicians': available_technicians,
            'busy_technicians': busy_technicians,
            'utilization_rate': f"{(busy_technicians/total_technicians*100):.1f}%" if total_technicians > 0 else "0%"
        },
        'technicians': workload_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_technicians(request):
    """
    Get list of available technicians for assignment
    
    GET /api/shop/technicians/available/
    """
    available_techs = Employee.objects.filter(
        role__icontains='technician'
    ).select_related('shop')
    
    available_list = []
    
    for tech in available_techs:
        if tech.is_available:
            available_list.append({
                'id': tech.id,
                'name': tech.name,
                'role': tech.role,
                'current_workload': tech.workload_count,
                'max_capacity': 3,
                'appointments_today': tech.appointments_today.count()
            })
    
    return Response({
        'message': f'Found {len(available_list)} available technicians',
        'available_technicians': available_list
    }, status=status.HTTP_200_OK)


# URL patterns to add to shop/urls.py:
"""
Add these to your urlpatterns in shop/urls.py:

    # Technician allocation endpoints
    path("appointments/<int:appointment_id>/assign-technician/", 
         views.assign_technician, name="assign_technician"),
    path("appointments/<int:appointment_id>/start-work/", 
         views.start_work, name="start_work"),
    path("appointments/<int:appointment_id>/complete-work/", 
         views.complete_work, name="complete_work"),
    path("technicians/workload/", 
         views.technician_workload, name="technician_workload"),
    path("technicians/available/", 
         views.available_technicians, name="available_technicians"),
"""
