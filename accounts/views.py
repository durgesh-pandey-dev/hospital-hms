import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)
        if role == 'doctor':
            return redirect('doctor_dashboard')
        return redirect('patient_dashboard')
    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            requests.post('http://127.0.0.1:3000/send-email', json={
    'trigger': 'SIGNUP_WELCOME',
    'email': email,
    'name': username
}, timeout=5)
            if user.role == 'doctor':
                return redirect('doctor_dashboard')
            return redirect('patient_dashboard')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')