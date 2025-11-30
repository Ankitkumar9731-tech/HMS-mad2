from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from models import db, Doctor, Patient, Appointment, Treatment, Medicine, DoctorAvailability
from utils import role_required

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@role_required(['doctor'])
def dashboard():
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('auth.logout'))
    
    today = datetime.now().date()
    
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == 'Booked',
        Appointment.appointment_date >= today
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    # Get assigned patients (patients who have appointments with this doctor)
    assigned_patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         upcoming_appointments=upcoming_appointments,
                         assigned_patients=assigned_patients)

@doctor_bp.route('/availability', methods=['GET', 'POST'])
@role_required(['doctor'])
def availability():
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('auth.logout'))
    
    if request.method == 'POST':
        # Clear existing availability for next 7 days
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=6)
        DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor.id,
            DoctorAvailability.date >= start_date,
            DoctorAvailability.date <= end_date
        ).delete()
        
        # Add new availability
        for i in range(7):
            date = start_date + timedelta(days=i)
            morning = request.form.get(f'morning_{i}') == 'on'
            evening = request.form.get(f'evening_{i}') == 'on'
            
            if morning or evening:
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    date=date,
                    morning_slot=morning,
                    evening_slot=evening
                )
                db.session.add(availability)
        
        db.session.commit()
        flash('Availability updated successfully!', 'success')
        return redirect(url_for('doctor.availability'))
    
    # Get availability for next 7 days
    start_date = datetime.now().date()
    dates = []
    availabilities = {}
    for i in range(7):
        date = start_date + timedelta(days=i)
        dates.append(date)
        avail = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=date).first()
        availabilities[date] = avail
    
    return render_template('doctor/availability.html', doctor=doctor, dates=dates, availabilities=availabilities)

@doctor_bp.route('/appointments/<int:appointment_id>/update', methods=['GET', 'POST'])
@role_required(['doctor'])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    if appointment.doctor_id != doctor.id:
        flash('You do not have permission to update this appointment.', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'complete':
            appointment.status = 'Completed'
            
            # Create or update treatment
            treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()
            if not treatment:
                treatment = Treatment(appointment_id=appointment.id)
                db.session.add(treatment)
            
            treatment.visit_type = request.form.get('visit_type')
            treatment.tests_done = request.form.get('tests_done')
            treatment.diagnosis = request.form.get('diagnosis')
            treatment.prescription = request.form.get('prescription')
            treatment.notes = request.form.get('notes')
            
            # Handle medicines
            Medicine.query.filter_by(treatment_id=treatment.id).delete()
            medicine_names = request.form.getlist('medicine_name[]')
            dosages = request.form.getlist('dosage[]')
            
            for name, dosage in zip(medicine_names, dosages):
                if name.strip():
                    medicine = Medicine(treatment_id=treatment.id, medicine_name=name, dosage=dosage)
                    db.session.add(medicine)
            
            db.session.commit()
            flash('Appointment marked as completed and treatment history updated!', 'success')
        
        elif action == 'cancel':
            appointment.status = 'Cancelled'
            db.session.commit()
            flash('Appointment cancelled!', 'success')
        
        return redirect(url_for('doctor.dashboard'))
    
    treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()
    return render_template('doctor/update_appointment.html', appointment=appointment, treatment=treatment)

@doctor_bp.route('/patients/<int:patient_id>/history')
@role_required(['doctor'])
def view_patient_history(patient_id):
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    patient = Patient.query.get_or_404(patient_id)
    
    # Get all appointments for this patient with this doctor
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.doctor_id == doctor.id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/patient_history.html', patient=patient, appointments=appointments, doctor=doctor)

