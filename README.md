# 🏥 Hospital Management System

A comprehensive web-based Hospital Management System built with Flask that streamlines hospital operations including patient registration, appointment scheduling, doctor management, and administrative controls.

## ✨ Features

### 👥 Multi-Role System
- **Admin Dashboard**: Complete control over doctors, patients, and system operations
- **Doctor Portal**: Manage appointments, availability schedules, and patient records
- **Patient Portal**: Book appointments, view medical history, and manage profiles

### 🔐 Authentication & Security
- Secure user authentication with password hashing
- Role-based access control (Admin, Doctor, Patient)
- Session management for secure access

### 📅 Appointment Management
- Real-time appointment booking system
- Doctor availability scheduling
- Appointment status tracking (Scheduled, Completed, Cancelled)
- Medical records (diagnosis and prescription) storage

### 👨‍⚕️ Doctor Management
- Add, edit, and remove doctor accounts
- Department and specialization tracking
- Experience years recording
- Availability slot management

### 📊 Administrative Features
- View all patients and doctors
- Manage contact messages
- Delete user accounts
- Edit doctor information

### 📧 Contact System
- Contact form for visitor inquiries
- Message storage and management
- Admin notification system

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Werkzeug password hashing
- **Forms**: Flask-WTF

## 📋 Database Schema

The system uses 5 main database tables:
- **Users**: Stores all user accounts (Admin, Doctor, Patient)
- **DoctorDetail**: Professional information for doctors
- **Appointment**: Appointment records and medical data
- **ContactMessage**: Messages from contact form
- **DoctorAvailability**: Doctor schedule management

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/1samyak/Hospital-Management-System.git
   cd Hospital-Management-System
   ```

2. **Install required packages**
   ```bash
   pip install flask
   pip install flask-sqlalchemy
   pip install werkzeug
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin`

## 📖 Usage Guide

### For Administrators

1. **Login** with admin credentials
2. **Add Doctors**: Navigate to admin dashboard and fill in doctor details
3. **Manage Users**: View, edit, or delete doctor/patient accounts
4. **View Messages**: Check contact form submissions

### For Doctors

1. **Register/Login** to the doctor portal
2. **Set Availability**: Configure your schedule and time slots
3. **View Appointments**: See upcoming and past appointments
4. **Complete Appointments**: Add diagnosis and prescriptions after consultations

### For Patients

1. **Register** a new patient account
2. **Login** to the patient portal
3. **Book Appointments**: Select a doctor and preferred time
4. **View History**: Check past appointments and medical records
5. **Update Profile**: Manage personal information

## 📁 Project Structure

```
Hospital-Management-System/
│
├── app.py                 # Main application file with all routes
├── models.py             # Database models (User, Doctor, Appointment, etc.)
├── config.py             # Configuration settings
├── test.py               # Testing utilities
│
├── static/               # Static files
│   ├── css/
│   │   └── style.css    # Application styles
│   └── images/
│       └── logo.png     # Hospital logo
│
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Homepage
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── about.html      # About page
│   ├── contact.html    # Contact page
│   ├── doctors.html    # Doctors listing
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── edit_doctor.html
│   │
│   ├── doctor/
│   │   └── dashboard.html
│   │
│   └── patient/
│       ├── dashboard.html
│       └── profile.html
│
└── instance/
    └── hospital.db      # SQLite database
```

## 🔑 Key Functionalities

### Authentication Flow
1. Users register with username, email, and password
2. Passwords are securely hashed using Werkzeug
3. Login validates credentials and creates sessions
4. Role-based redirects to appropriate dashboards

### Appointment Booking Flow
1. Patient selects a doctor from available list
2. Chooses date and time from doctor's availability
3. System creates appointment with "Scheduled" status
4. Doctor can later update with diagnosis and prescription

### Doctor Availability Management
1. Doctors can set weekly availability slots
2. Each slot has day, start time, and end time
3. Availability can be toggled on/off
4. Patients see only available doctors when booking

## 🔒 Security Features

- Password hashing with Werkzeug security
- Session-based authentication
- Role-based access control
- SQL injection prevention via SQLAlchemy ORM
- CSRF protection ready (extensible)

## 🐛 Known Issues & Future Enhancements

- Email notifications for appointments (planned)
- Payment integration (planned)
- Patient medical history reports (planned)
- Doctor ratings and reviews (planned)
- Mobile responsive design improvements (in progress)

## 👨‍💻 Author

**Samyak**
- GitHub: [@1samyak](https://github.com/1samyak)

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📞 Support

For support or queries, use the contact form in the application or raise an issue on GitHub.

---

**Note**: This is a demo application for educational purposes. For production use, additional security measures, error handling, and testing should be implemented.
