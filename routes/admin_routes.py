from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, User, Doctor, Patient, Appointment, Department
from utils import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required(['admin'])
def dashboard():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    upcoming_appointments = Appointment.query.filter(
        Appointment.status == 'Booked',
        Appointment.appointment_date >= datetime.now().date()
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         upcoming_appointments=upcoming_appointments)

@admin_bp.route('/doctors')
@role_required(['admin'])
def doctors():
    search = request.args.get('search', '')
    doctors = Doctor.query.join(User).filter(User.is_blacklisted == False)
    
    if search:
        doctors = doctors.filter(
            db.or_(
                Doctor.fullname.contains(search),
                Doctor.specialization.contains(search)
            )
        )
    
    doctors = doctors.all()
    return render_template('admin/doctors.html', doctors=doctors, search=search)

@admin_bp.route('/doctors/add', methods=['GET', 'POST'])
@role_required(['admin'])
def add_doctor():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        specialization = request.form.get('specialization')
        experience = request.form.get('experience', type=int)
        qualifications = request.form.get('qualifications')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/add_doctor.html', departments=Department.query.all())
        
        # Create user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()
        
        # Get or create department
        department = Department.query.filter_by(name=specialization).first()
        if not department:
            department = Department(name=specialization, description=f'{specialization} department')
            db.session.add(department)
            db.session.flush()
        
        # Create doctor
        doctor = Doctor(
            user_id=user.id,
            fullname=fullname,
            specialization=specialization,
            department_id=department.id,
            experience=experience,
            qualifications=qualifications or ''
        )
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/add_doctor.html', departments=Department.query.all())

@admin_bp.route('/doctors/<int:doctor_id>/edit', methods=['GET', 'POST'])
@role_required(['admin'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        doctor.fullname = request.form.get('fullname')
        doctor.specialization = request.form.get('specialization')
        doctor.experience = request.form.get('experience', type=int)
        doctor.qualifications = request.form.get('qualifications')
        
        # Update department
        department = Department.query.filter_by(name=doctor.specialization).first()
        if not department:
            department = Department(name=doctor.specialization, description=f'{doctor.specialization} department')
            db.session.add(department)
            db.session.flush()
        doctor.department_id = department.id
        
        db.session.commit()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('admin.doctors'))
    
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=Department.query.all())

@admin_bp.route('/doctors/<int:doctor_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/doctors/<int:doctor_id>/blacklist', methods=['POST'])
@role_required(['admin'])
def blacklist_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.user.is_blacklisted = True
    db.session.commit()
    flash('Doctor blacklisted successfully!', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/patients')
@role_required(['admin'])
def patients():
    search = request.args.get('search', '')
    patients = Patient.query.join(User).filter(User.is_blacklisted == False)
    
    if search:
        patients = patients.filter(
            db.or_(
                Patient.fullname.contains(search),
                Patient.email.contains(search),
                Patient.phone.contains(search)
            )
        )
    
    patients = patients.all()
    return render_template('admin/patients.html', patients=patients, search=search)

@admin_bp.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@role_required(['admin'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        patient.fullname = request.form.get('fullname')
        patient.email = request.form.get('email')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('admin.patients'))
    
    return render_template('admin/edit_patient.html', patient=patient)

@admin_bp.route('/patients/<int:patient_id>/delete', methods=['POST'])
@role_required(['admin'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    user = patient.user
    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('admin.patients'))

@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['POST'])
@role_required(['admin'])
def blacklist_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.user.is_blacklisted = True
    db.session.commit()
    flash('Patient blacklisted successfully!', 'success')
    return redirect(url_for('admin.patients'))

@admin_bp.route('/appointments')
@role_required(['admin'])
def appointments():
    appointments = Appointment.query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time
    ).all()
    return render_template('admin/appointments.html', appointments=appointments)

@admin_bp.route('/appointments/<int:appointment_id>/history')
@role_required(['admin'])
def view_patient_history(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = appointment.patient
    
    # Get all appointments for this patient
    all_appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('admin/patient_history.html', patient=patient, appointments=all_appointments)

