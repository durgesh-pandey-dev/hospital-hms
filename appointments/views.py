from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from .models import AvailabilitySlot, Booking
from accounts.models import User
import requests

def trigger_email(trigger, email, **kwargs):
    try:
        requests.post('http://localhost:3000/dev/send-email', json={
            'trigger': trigger,
            'email': email,
            **kwargs
        }, timeout=5)
    except:
        pass

@login_required
def doctor_dashboard(request):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
    slots = AvailabilitySlot.objects.filter(doctor=request.user)
    return render(request, 'appointments/doctor_dashboard.html', {'slots': slots})

@login_required
def add_slot(request):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        AvailabilitySlot.objects.create(
            doctor=request.user,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('doctor_dashboard')
    return render(request, 'appointments/add_slot.html')

@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
    doctors = User.objects.filter(role='doctor')
    return render(request, 'appointments/patient_dashboard.html', {'doctors': doctors})

@login_required
def view_slots(request, doctor_id):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
    doctor = get_object_or_404(User, id=doctor_id, role='doctor')
    slots = AvailabilitySlot.objects.filter(doctor=doctor, is_booked=False)
    return render(request, 'appointments/view_slots.html', {'doctor': doctor, 'slots': slots})

@login_required
def book_slot(request, slot_id):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
    if request.method == 'POST':
        with transaction.atomic():
            slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
            if slot.is_booked:
                return render(request, 'appointments/error.html', {'message': 'Slot already booked!'})
            slot.is_booked = True
            slot.save()
            booking = Booking.objects.create(patient=request.user, slot=slot)
            trigger_email(
                'BOOKING_CONFIRMATION',
                request.user.email,
                doctor_name=slot.doctor.username,
                date=str(slot.date),
                time=str(slot.start_time)
            )
        return redirect('patient_dashboard')
    slot = get_object_or_404(AvailabilitySlot, id=slot_id)
    return render(request, 'appointments/book_slot.html', {'slot': slot})