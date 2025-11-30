from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from models import db, Patient, Doctor, Department, Appointment, DoctorAvailability
from utils import role_required

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@role_required(['patient'])
def dashboard():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Get all departments
    departments = Department.query.all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Booked',
        Appointment.appointment_date >= datetime.now().date()
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         departments=departments,
                         upcoming_appointments=upcoming_appointments)

@patient_bp.route('/departments/<int:department_id>')
@role_required(['patient'])
def department_view(department_id):
    from models import User
    department = Department.query.get_or_404(department_id)
    doctors = Doctor.query.filter_by(department_id=department.id).join(User).filter(
        User.is_blacklisted == False
    ).all()
    
    return render_template('patient/department.html', department=department, doctors=doctors)

@patient_bp.route('/doctors/<int:doctor_id>')
@role_required(['patient'])
def doctor_view(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.user.is_blacklisted:
        flash('This doctor is not available.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    return render_template('patient/doctor_profile.html', doctor=doctor)

@patient_bp.route('/doctors/<int:doctor_id>/availability')
@role_required(['patient'])
def doctor_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.user.is_blacklisted:
        flash('This doctor is not available.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    # Get availability for next 7 days
    start_date = datetime.now().date()
    dates = []
    availabilities = {}
    for i in range(7):
        date = start_date + timedelta(days=i)
        dates.append(date)
        avail = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=date).first()
        if avail:
            # Check how many appointments are booked
            morning_count = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == date,
                Appointment.appointment_time == '08:00-12:00',
                Appointment.status == 'Booked'
            ).count()
            
            evening_count = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == date,
                Appointment.appointment_time == '16:00-21:00',
                Appointment.status == 'Booked'
            ).count()
            
            avail.morning_booked = morning_count
            avail.evening_booked = evening_count
        
        availabilities[date] = avail
    
    return render_template('patient/doctor_availability.html', doctor=doctor, dates=dates, availabilities=availabilities)

@patient_bp.route('/appointments/book', methods=['POST'])
@role_required(['patient'])
def book_appointment():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    doctor_id = request.form.get('doctor_id', type=int)
    appointment_date = request.form.get('appointment_date')
    appointment_time = request.form.get('appointment_time')
    
    if not doctor_id or not appointment_date or not appointment_time:
        flash('Please fill all fields.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    
    appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Check if doctor has availability for this slot
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id,
        date=appointment_date
    ).first()
    
    if not availability:
        flash('Doctor is not available on this date.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    
    # Check slot availability
    if appointment_time == '08:00-12:00' and not availability.morning_slot:
        flash('Morning slot is not available.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    
    if appointment_time == '16:00-21:00' and not availability.evening_slot:
        flash('Evening slot is not available.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    
    # Check for conflicts (same doctor, same date, same time)
    existing = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status == 'Booked'
    ).count()
    
    max_appointments = availability.max_appointments_per_slot
    if existing >= max_appointments:
        flash('This time slot is fully booked. Please choose another slot.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    
    # Check if patient already has an appointment at this time
    patient_conflict = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status == 'Booked'
    ).first()
    
    if patient_conflict:
        flash('You already have an appointment at this time.', 'danger')
        return redirect(url_for('patient.doctor_availability', doctor_id=doctor_id))
    
    # Create appointment
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status='Booked'
    )
    db.session.add(appointment)
    db.session.commit()
    
    flash('Appointment booked successfully!', 'success')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@role_required(['patient'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    if appointment.patient_id != patient.id:
        flash('You do not have permission to cancel this appointment.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    if appointment.status != 'Booked':
        flash('Only booked appointments can be cancelled.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/history')
@role_required(['patient'])
def history():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    # Get all appointments
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('patient/history.html', patient=patient, appointments=appointments)

@patient_bp.route('/profile', methods=['GET', 'POST'])
@role_required(['patient'])
def profile():
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        patient.fullname = request.form.get('fullname')
        patient.email = request.form.get('email')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/profile.html', patient=patient)

