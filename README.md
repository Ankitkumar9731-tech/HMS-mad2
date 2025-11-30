# Hospital Management System (HMS)

A comprehensive web application for managing hospital operations, built with Flask, SQLite, and Bootstrap.

## Features

### Admin Functionalities

- **Dashboard**: View total doctors, patients, and appointments
- **Doctor Management**: Add, update, delete, and blacklist doctors
- **Patient Management**: View, edit, delete, and blacklist patients
- **Appointment Management**: View all appointments and patient history
- **Search**: Search for doctors, patients, and departments

### Doctor Functionalities

- **Dashboard**: View upcoming appointments and assigned patients
- **Availability Management**: Set availability for the next 7 days (morning and evening slots)
- **Appointment Management**: Mark appointments as completed or cancelled
- **Patient History**: View and update patient treatment history
- **Treatment Records**: Add diagnosis, prescriptions, tests, and medicines

### Patient Functionalities

- **Registration & Login**: Self-registration and profile management
- **Department Browsing**: View all available departments
- **Doctor Search**: Browse doctors by department and view profiles
- **Appointment Booking**: Book appointments based on doctor availability
- **Appointment Management**: View and cancel upcoming appointments
- **Medical History**: View complete treatment history with diagnoses and prescriptions

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap 5, Jinja2 Templates
- **Database**: SQLite
- **Authentication**: Session-based with password hashing

## Installation

1. **Clone or download the project**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:

   ```bash
   python app.py
   ```

4. **Access the application**:
   - Open your browser and navigate to `http://localhost:5000`

## Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

**Note**: Change the admin password after first login in a production environment.

## Database

The database (`hospital.db`) is created automatically when you first run the application. All tables and the admin user are created programmatically.

## Project Structure

```
HMS mad1/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── hospital.db           # SQLite database (created automatically)
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── admin/            # Admin templates
│   ├── doctor/           # Doctor templates
│   └── patient/          # Patient templates
└── static/               # Static files (CSS, JS, images)
```

## Key Features Implementation

### Appointment Conflict Prevention

- Prevents multiple appointments at the same date and time for the same doctor
- Checks slot capacity before booking
- Prevents patients from booking multiple appointments at the same time

### Appointment Status Management

- **Booked**: Initial status when appointment is created
- **Completed**: Set by doctor after treatment
- **Cancelled**: Can be set by doctor or patient

### Patient History

- Complete treatment records stored for each visit
- Includes diagnosis, prescriptions, tests, and medicines
- Accessible by patients, doctors, and admins

### Doctor Availability

- 7-day rolling availability window
- Morning slot: 08:00 - 12:00
- Evening slot: 16:00 - 21:00
- Real-time booking capacity tracking

## Usage Guide

### For Admins

1. Login with admin credentials
2. Add doctors through "Manage Doctors"
3. View and manage all appointments
4. Search for patients or doctors
5. Blacklist users if needed

### For Doctors

1. Login with doctor credentials (created by admin)
2. Set availability for the next 7 days
3. View upcoming appointments
4. Update patient history after consultations
5. Mark appointments as completed

### For Patients

1. Register a new account or login
2. Browse departments and doctors
3. Check doctor availability
4. Book appointments
5. View treatment history

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- Blacklist functionality for users
- Input validation and sanitization

## Notes

- All database operations are performed programmatically
- No manual database creation required
- Admin user is created automatically on first run
- The application is designed for local development and demonstration

## Future Enhancements

Potential improvements:

- Email notifications for appointments
- PDF report generation for patient history
- Advanced search and filtering
- Appointment reminders
- Multi-language support
- Mobile-responsive optimizations

## License

This project is created for educational purposes.
