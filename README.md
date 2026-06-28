# Hospital Management System (HMS)

A mini Hospital Management System built with Django and PostgreSQL, featuring doctor availability management, patient appointment booking, and email notifications.

## Setup and Run

### Prerequisites
- Python 3.12+
- PostgreSQL
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tumhara-username/hospital-hms.git
cd hospital-hms
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE hms_db;
\q
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start Django app:
```bash
python manage.py runserver
```

7. In a new terminal, start email service:
```bash
python email-service.py
```

8. Visit: http://127.0.0.1:8000

## System Architecture

### Components
- **Django App**: Handles authentication, doctor availability, and patient booking
- **PostgreSQL**: Primary database for all data
- **Flask Email Service**: Separate microservice running on port 3000 for email notifications

### Data Models
- **User**: Extended Django AbstractUser with role field (doctor/patient)
- **AvailabilitySlot**: Doctor's available time slots with date, start_time, end_time, is_booked
- **Booking**: Links patient to a booked slot

### Role-Based Access
- Doctors can only access doctor dashboard and manage their own slots
- Patients can only access patient dashboard and book appointments
- Enforced via role checks in every view

### Email Service
- Separate Flask microservice on port 3000
- Django backend calls it via HTTP POST
- Supports SIGNUP_WELCOME and BOOKING_CONFIRMATION triggers

## The Design Decision

### Problem: Handling Race Conditions in Slot Booking

When two patients attempt to book the same slot simultaneously, a naive implementation would allow both bookings to succeed — creating a double-booking bug.

### Option 1: Application-Level Check
Check `if slot.is_booked` before creating booking. Simple to implement but fails under concurrency — both requests can pass the check before either saves to the database.

### Option 2: Database-Level Row Locking with select_for_update()
Use PostgreSQL's row-level locking inside a transaction:

```python
with transaction.atomic():
    slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
    if slot.is_booked:
        return error
    slot.is_booked = True
    slot.save()
```

### My Choice: Option 2

Database-level locking is the only correct solution. Application-level checks create a TOCTOU (Time-of-Check-Time-of-Use) vulnerability. PostgreSQL's `select_for_update()` locks the row at the database level — the second request waits until the first transaction completes. Only one booking can ever succeed for a given slot. The minor performance cost of lock wait time is completely acceptable for a booking system where correctness is non-negotiable.

## Limitations

### What Would Break in Production

1. **Email service is not truly serverless** — replaced Serverless Framework with Flask microservice due to Node.js compatibility issues. In production, this would be AWS Lambda or similar.

2. **No Google Calendar integration** — skipped due to time constraints. Would implement OAuth2 token storage per user and Google Calendar API calls on booking confirmation.

3. **No HTTPS** — session cookies are vulnerable without SSL in production.

4. **Single server** — Django's development server cannot handle production load. Would need Gunicorn + Nginx.

5. **Credentials via environment variables** — currently need to be set manually. Would use proper secrets management in production.