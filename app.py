"""
Hospital Management System - Main Application File
Author: Samyak
Description: Web application for managing hospital operations including patient registration,
             doctor appointments, admin controls, and contact management.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, DoctorDetail, Appointment, ContactMessage, DoctorAvailability
from datetime import datetime

# Initialize Flask application with a descriptive name
hms_app = Flask(__name__)

# Configure application settings
hms_app.config['SECRET_KEY'] = 'medicore24'  # Secret key for session management and CSRF protection
hms_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'  # SQLite database location
hms_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable overhead of tracking modifications

# Link SQLAlchemy database instance to Flask app
db.init_app(hms_app)


@hms_app.route('/') 
def index():
    """
    Homepage route.
    Returns: Renders the main landing page template
    """
    return render_template('index.html')


@hms_app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user authentication for all roles (Admin, Doctor, Patient).
    
    GET: Displays login form
    POST: Validates credentials and creates session
    
    Returns: Redirects to role-specific dashboard or shows login form with errors
    """
    if request.method == 'POST':
        # Retrieve login credentials from submitted form
        username_input = request.form['username']
        password_input = request.form['password']
        
        # Query database for matching username
        user_record = User.query.filter_by(username=username_input).first()
        
        # Verify password hash and authenticate user
        if user_record and check_password_hash(user_record.password, password_input):
            # Store user information in session for authorization
            session['user_id'] = user_record.id
            session['role'] = user_record.role
            session['username'] = user_record.username
            
            # Route user to appropriate dashboard based on their role
            if user_record.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_record.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user_record.role == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            flash("Invalid username or password")
            
    return render_template('login.html')


@hms_app.route('/logout')
def logout():
    """
    Terminates user session and returns to login page.
    
    Returns: Redirect to login page
    """
    session.clear()
    return redirect(url_for('login'))


@hms_app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Patient self-registration endpoint.
    
    GET: Shows registration form
    POST: Creates new patient account with hashed password
    
    Returns: Redirects to login on success, shows form with errors on failure
    """
    if request.method == 'POST':
        username_input = request.form['username']
        password_input = request.form['password']
        email_input = request.form['email']
        account_type = 'patient'  # New registrations are always patients
        
        # Check for username conflicts
        duplicate_check = User.query.filter_by(username=username_input).first()
        if duplicate_check:
            flash("Username already exists. Please choose another.")
        else:
            # Hash password before storing for security
            secure_password = generate_password_hash(password_input)
            new_patient = User(username=username_input, password=secure_password, 
                          email=email_input, role=account_type)
            db.session.add(new_patient)
            db.session.commit()
            flash("Account created successfully! You can now log in.")
            return redirect(url_for('login'))
            
    return render_template('register.html')


@hms_app.route('/admin/dashboard')
def admin_dashboard():
    """
    Administrator control panel.
    Displays lists of doctors, patients, and recent contact messages.
    
    Returns: Admin dashboard template with data
    """
    # Ensure only admin users can access this page
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Fetch all doctors and patients for display
    all_doctors = User.query.filter_by(role='doctor').all()
    all_patients = User.query.filter_by(role='patient').all()
    
    # Get recent contact form submissions, newest first
    recent_messages = ContactMessage.query.order_by(ContactMessage.date_sent.desc()).all()
    
    return render_template('admin/dashboard.html', 
                         doctors=all_doctors, 
                         patients=all_patients, 
                         messages=recent_messages)


@hms_app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    """
    Creates a new doctor account with professional details.
    Only accessible by administrators.
    
    Returns: Redirects to admin dashboard
    """
    # Authorization check
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Extract basic account information
    doctor_username = request.form['username']
    doctor_email = request.form['email']
    doctor_password = request.form['password']
    
    # Create user account with hashed password
    hashed_pwd = generate_password_hash(doctor_password)
    doctor_account = User(username=doctor_username, email=doctor_email, 
                      password=hashed_pwd, role='doctor')
    db.session.add(doctor_account)
    db.session.commit()
    
    # Extract professional qualifications
    doctor_department = request.form['department']
    doctor_specialization = request.form['specialization']
    years_experience = request.form['experience']
    
    # Link professional details to user account
    professional_info = DoctorDetail(user_id=doctor_account.id, 
                                    department=doctor_department, 
                                    specialization=doctor_specialization, 
                                    experience=years_experience)
    db.session.add(professional_info)
    db.session.commit()
    
    flash("Doctor profile created successfully")
    return redirect(url_for('admin_dashboard'))


@hms_app.route('/doctor/dashboard')
def doctor_dashboard():
    """
    Doctor workspace showing scheduled appointments and availability.
    
    Returns: Doctor dashboard template with appointment list and availability
    """
    # Verify doctor authentication
    if session.get('role') != 'doctor':
        return redirect(url_for('login'))
    
    current_doctor = session['user_id']
    
    # Load all appointments assigned to this doctor
    my_appointments = Appointment.query.filter_by(doctor_id=current_doctor).all()
    
    # Get doctor's availability slots
    availability = DoctorAvailability.query.filter_by(doctor_id=current_doctor).all()
    
    # If no availability exists, create default time slots (Monday-Friday, 9 AM - 5 PM)
    if not availability:
        default_slots = []
        time_slots = [
            ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00"), 
            ("12:00", "13:00"), ("14:00", "15:00"), ("15:00", "16:00"), 
            ("16:00", "17:00")
        ]
        for day in range(5):  # Monday to Friday
            for start, end in time_slots:
                slot = DoctorAvailability(
                    doctor_id=current_doctor,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    is_available=True
                )
                default_slots.append(slot)
                db.session.add(slot)
        db.session.commit()
        availability = default_slots
    
    # Group availability by day for easier template rendering
    availability_by_day = {}
    for slot in availability:
        if slot.day_of_week not in availability_by_day:
            availability_by_day[slot.day_of_week] = []
        availability_by_day[slot.day_of_week].append(slot)
    
    return render_template('doctor/dashboard.html', 
                         appointments=my_appointments,
                         availability=availability_by_day)



@hms_app.route('/doctor/complete_appointment/<int:id>', methods=['POST'])
def complete_appointment(id):
    """
    Allows doctor to update patient records after consultation.
    
    Args:
        id: Appointment ID to update
        
    Returns: Redirects to doctor dashboard
    """
    # Retrieve the specific appointment
    appointment_record = Appointment.query.get_or_404(id)
    
    # Update medical information from form
    appointment_record.diagnosis = request.form['diagnosis']
    appointment_record.prescription = request.form['prescription']
    appointment_record.status = 'Completed'
    
    db.session.commit()
    flash("Patient record updated successfully")
    return redirect(url_for('doctor_dashboard'))


@hms_app.route('/doctor/toggle_availability/<int:slot_id>', methods=['POST'])
def toggle_availability(slot_id):
    """
    Toggles the availability status of a specific time slot.
    
    Args:
        slot_id: Availability slot ID to toggle
        
    Returns: Redirects to doctor dashboard
    """
    # Verify doctor authentication
    if session.get('role') != 'doctor':
        return redirect(url_for('login'))
    
    # Get the slot and verify it belongs to this doctor
    slot = DoctorAvailability.query.get_or_404(slot_id)
    
    if slot.doctor_id != session['user_id']:
        flash("Unauthorized access")
        return redirect(url_for('doctor_dashboard'))
    
    # Toggle availability
    slot.is_available = not slot.is_available
    db.session.commit()
    
    status = "available" if slot.is_available else "unavailable"
    flash(f"Time slot {slot.start_time}-{slot.end_time} marked as {status}")
    return redirect(url_for('doctor_dashboard'))




@hms_app.route('/patient/dashboard')
def patient_dashboard():
    """
    Patient portal showing available doctors and appointment history.
    
    Returns: Patient dashboard template
    """
    # Check patient authentication
    if session.get('role') != 'patient':
        return redirect(url_for('login'))
    
    # Get list of all doctors for booking
    doctors_list = User.query.filter_by(role='doctor').all()
    
    # Retrieve this patient's appointment history
    my_appointments = Appointment.query.filter_by(patient_id=session['user_id']).all()
    
    return render_template('patient/dashboard.html', 
                         doctors=doctors_list, 
                         history=my_appointments)


@hms_app.route('/patient/profile', methods=['GET', 'POST'])
def patient_profile():
    """
    Patient profile management page.
    Allows patients to view and update their account information.
    
    Returns: Profile page template
    """
    if session.get('role') != 'patient':
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # Update basic information
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        
        # Update password if provided
        new_pwd = request.form['new_password']
        if new_pwd:
            current_user.password = generate_password_hash(new_pwd)
            
        try:
            db.session.commit()
            flash("Profile updated successfully")
        except:
            db.session.rollback()
            flash("Error updating profile. Username or Email might already exist.")
            
        return redirect(url_for('patient_profile'))
        
    return render_template('patient/profile.html', user=current_user)


@hms_app.route('/patient/book', methods=['POST'])
def book_appointment():
    """
    Creates a new appointment booking for a patient.
    
    Returns: Redirects to patient dashboard
    """
    doctor_selection = request.form['doctor_id']
    appointment_date = request.form['date']
    
    # Create new appointment record
    new_booking = Appointment(
        patient_id=session['user_id'],
        doctor_id=doctor_selection,
        date=datetime.strptime(appointment_date, '%Y-%m-%d'),
        status='Scheduled'
    )
    
    db.session.add(new_booking)
    db.session.commit()
    flash("Your appointment has been scheduled")
    return redirect(url_for('patient_dashboard'))


@hms_app.route('/about')
def about():
    """
    Hospital information page.
    
    Returns: About page template
    """
    return render_template('about.html')


@hms_app.route('/doctors')
def doctors():
    """
    Public directory of all doctors.
    
    Returns: Doctors listing page
    """
    all_doctors = User.query.filter_by(role='doctor').all()
    return render_template('doctors.html', doctors=all_doctors)


@hms_app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact form for visitors to send messages to hospital administration.
    
    GET: Shows contact form
    POST: Saves message to database
    
    Returns: Contact page template
    """
    if request.method == 'POST':
        # Combine first and last name
        sender_name = f"{request.form['firstname']} {request.form['lastname']}"
        sender_email = request.form['email']
        message_subject = request.form['subject']
        message_text = request.form['message']
        
        # Store message in database for admin review
        incoming_message = ContactMessage(name=sender_name, 
                                        email=sender_email, 
                                        subject=message_subject, 
                                        message=message_text)
        db.session.add(incoming_message)
        db.session.commit()
        
        flash("Thank you for your message! We will get back to you soon.")
        return redirect(url_for('contact'))
    return render_template('contact.html')


@hms_app.route('/admin/delete_doctor/<int:id>')
def delete_doctor(id):
    """
    Removes a doctor account and associated profile.
    Admin-only function.
    
    Args:
        id: Doctor user ID to delete
        
    Returns: Redirects to admin dashboard
    """
    # Security verification
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Locate doctor account
    doctor_account = User.query.get(id)
    if doctor_account and doctor_account.role == 'doctor':
        # Remove professional profile first (foreign key constraint)
        if doctor_account.doctor_profile:
            db.session.delete(doctor_account.doctor_profile)
        # Remove user account
        db.session.delete(doctor_account)
        db.session.commit()
        flash(f"Dr. {doctor_account.username} has been removed successfully")
    else:
        flash("Doctor not found")
    
    return redirect(url_for('admin_dashboard'))


@hms_app.route('/admin/delete_patient/<int:id>')
def delete_patient(id):
    """
    Removes a patient account and all associated appointments.
    Admin-only function.
    
    Args:
        id: Patient user ID to delete
        
    Returns: Redirects to admin dashboard
    """
    # Authorization check
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Find patient account
    patient_account = User.query.get(id)
    if patient_account and patient_account.role == 'patient':
        # Delete appointment history first
        Appointment.query.filter_by(patient_id=id).delete()
        # Delete patient account
        db.session.delete(patient_account)
        db.session.commit()
        flash(f"Patient {patient_account.username} has been removed")
    else:
        flash("Patient not found")
    
    return redirect(url_for('admin_dashboard'))


@hms_app.route('/admin/blacklist_doctor/<int:id>')
def blacklist_doctor(id):
    """
    Placeholder for future account suspension feature.
    Currently just displays a notification.
    
    Args:
        id: Doctor user ID
        
    Returns: Redirects to admin dashboard
    """
    # Security check
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    doctor_account = User.query.get(id)
    if doctor_account and doctor_account.role == 'doctor':
        # Note: In production, would set an 'is_active' flag to False
        flash(f"Dr. {doctor_account.username} has been blacklisted (feature in development)")
    
    return redirect(url_for('admin_dashboard'))


@hms_app.route('/admin/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    """
    Allows admin to modify doctor account and professional information.
    
    Args:
        id: Doctor user ID to edit
        
    Returns: Edit form on GET, redirects to dashboard on POST
    """
    # Verify admin access
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    doctor_account = User.query.get(id)
    if not doctor_account or doctor_account.role != 'doctor':
        flash("Doctor not found")
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Update basic account details
        doctor_account.username = request.form['username']
        doctor_account.email = request.form['email']
        
        # Update professional credentials
        doctor_account.doctor_profile.department = request.form['department']
        doctor_account.doctor_profile.specialization = request.form['specialization']
        doctor_account.doctor_profile.experience = request.form['experience']
        
        db.session.commit()
        flash(f"Dr. {doctor_account.username}'s profile updated successfully")
        return redirect(url_for('admin_dashboard'))
    
    # Display edit form with current data
    return render_template('admin/edit_doctor.html', doctor=doctor_account)


# Application initialization and startup
if __name__ == '__main__':
    with hms_app.app_context():
        # Initialize database schema
        db.create_all()
        
        # Create default admin account if it doesn't exist
        admin_check = User.query.filter_by(username='admin').first()
        if not admin_check:
            default_admin_account = User(username='admin', 
                                        email='admin@hms.com', 
                                        password=generate_password_hash('admin'), 
                                        role='admin')
            db.session.add(default_admin_account)
            db.session.commit()
            print("✓ Administrator account created (Username: admin, Password: admin)")
    
    # Launch Flask development server
    hms_app.run(debug=True)
