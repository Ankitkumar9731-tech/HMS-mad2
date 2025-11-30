"""
Script to add a doctor to the database
Run this script to add a doctor with the specified credentials
"""
from app import app, db
from models import User, Doctor, Department
from werkzeug.security import generate_password_hash

def add_doctor():
    with app.app_context():
        # Doctor details
        username = 'ankit12'
        password = 'Ankit@!@#'
        fullname = 'Dr. Ankit'
        specialization = 'General'
        experience = 5
        qualifications = 'MBBS'
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            print(f"Doctor with username '{username}' already exists!")
            return
        
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
            qualifications=qualifications
        )
        db.session.add(doctor)
        db.session.commit()
        
        print("=" * 50)
        print("Doctor added successfully!")
        print("=" * 50)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Fullname: {fullname}")
        print(f"Specialization: {specialization}")
        print(f"Experience: {experience} years")
        print("=" * 50)
        print("\nYou can now login with these credentials at:")
        print("http://localhost:5000/login")

if __name__ == '__main__':
    add_doctor()

