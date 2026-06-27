from django.urls import path
from . import views

urlpatterns = [
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/add-slot/', views.add_slot, name='add_slot'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/slots/<int:doctor_id>/', views.view_slots, name='view_slots'),
    path('patient/book/<int:slot_id>/', views.book_slot, name='book_slot'),
]