""" 
This file contains the database models for the Hospital Management System. 
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model): 
    """
    Represents a system user (Patient, Doctor, or Admin).
    Stores authentication details and role information.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    # Relationships
    doctor_profile = db.relationship('DoctorDetail', back_populates='user', uselist=False)
    appointments_as_patient = db.relationship('Appointment', foreign_keys='Appointment.patient_id', back_populates='patient')
    appointments_as_doctor = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', back_populates='doctor')
    
    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

class DoctorDetail(db.Model):
    """
    Stores specific professional details for users with the 'doctor' role.
    """
    __tablename__ = 'doctor_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    
    user = db.relationship('User', back_populates='doctor_profile')
    
    def __init__(self, user_id, department, specialization, experience):
        self.user_id = user_id
        self.department = department
        self.specialization = specialization
        self.experience = experience

class Appointment(db.Model):
    """
    Represents a medical appointment between a patient and a doctor.
    """
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Scheduled')
    
    # Medical Record Fields
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    
    patient = db.relationship('User', foreign_keys=[patient_id], back_populates='appointments_as_patient')
    doctor = db.relationship('User', foreign_keys=[doctor_id], back_populates='appointments_as_doctor')
    
    def __init__(self, patient_id, doctor_id, date, status='Scheduled', diagnosis=None, prescription=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.status = status
        self.diagnosis = diagnosis
        self.prescription = prescription

class ContactMessage(db.Model):
    """
    Stores messages submitted via the contact form.
    """
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, email, subject, message):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message

class DoctorAvailability(db.Model):
    """
    Stores doctor's availability schedule for time slots.
    """
    __tablename__ = 'doctor_availability'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.String(5), nullable=False)  # Format: "HH:MM"
    end_time = db.Column(db.String(5), nullable=False)    # Format: "HH:MM"
    is_available = db.Column(db.Boolean, default=True)
    
    doctor = db.relationship('User', backref='availability_slots')
    
    def __init__(self, doctor_id, day_of_week, start_time, end_time, is_available=True):
        self.doctor_id = doctor_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.is_available = is_available
