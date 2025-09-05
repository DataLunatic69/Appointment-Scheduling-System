import pandas as pd
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any
import os

EMAIL_TEMPLATES_FILE = "data/templates/email_templates.json"

# Email configuration - you'll need to set these as environment variables
GMAIL_USER = os.getenv("GMAIL_USER", "your_email@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "your_app_password")

def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email using Gmail SMTP server."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Create server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

def send_appointment_reminder(patient_id: str, appointment_id: str) -> str:
    """Send appointment reminder via email."""
    try:
        # Get patient info
        patients_df = pd.read_csv("data/patients.csv")
        patient = patients_df[patients_df['patient_id'] == patient_id]
        if patient.empty:
            return f"Patient with ID {patient_id} not found."
        
        # Get appointment info
        appointments_df = pd.read_excel("data/appointments.xlsx", sheet_name='Appointments')
        appointment = appointments_df[appointments_df['appointment_id'] == appointment_id]
        if appointment.empty:
            return f"Appointment with ID {appointment_id} not found."
        
        # Get doctor info
        doctors_df = pd.read_excel("data/appointments.xlsx", sheet_name='Doctors')
        doctor = doctors_df[doctors_df['doctor_id'] == appointment['doctor_id'].iloc[0]]
        doctor_name = doctor['name'].iloc[0] if not doctor.empty else "the doctor"
        
        # Load email templates
        with open(EMAIL_TEMPLATES_FILE, 'r') as f:
            templates = json.load(f)
        
        # Format message
        appointment_time = appointment['datetime'].iloc[0]
        template = templates.get('reminder', 'Your appointment with {doctor} is scheduled for {datetime}. Please arrive 15 minutes early.')
        message = template.format(doctor=doctor_name, datetime=appointment_time)
        
        # Send email
        patient_email = patient['email'].iloc[0]
        subject = "Appointment Reminder"
        result = send_email(patient_email, subject, message)
        
        return f"Reminder sent to patient {patient_id} for appointment {appointment_id}. {result}"
    except Exception as e:
        return f"Error sending reminder: {str(e)}"

def send_followup(patient_id: str, appointment_id: str) -> str:
    """Send follow-up message via email."""
    try:
        patients_df = pd.read_csv("data/patients.csv")
        patient = patients_df[patients_df['patient_id'] == patient_id]
        if patient.empty:
            return f"Patient with ID {patient_id} not found."
        
        # Get appointment info
        appointments_df = pd.read_excel("data/appointments.xlsx", sheet_name='Appointments')
        appointment = appointments_df[appointments_df['appointment_id'] == appointment_id]
        
        # Get doctor info if appointment exists
        doctor_name = "the doctor"
        if not appointment.empty:
            doctors_df = pd.read_excel("data/appointments.xlsx", sheet_name='Doctors')
            doctor = doctors_df[doctors_df['doctor_id'] == appointment['doctor_id'].iloc[0]]
            doctor_name = doctor['name'].iloc[0] if not doctor.empty else "the doctor"
        
        with open(EMAIL_TEMPLATES_FILE, 'r') as f:
            templates = json.load(f)
        
        template = templates.get('followup', 'Thank you for your appointment with {doctor}. How was your experience?')
        message = template.format(doctor=doctor_name)
        
        patient_email = patient['email'].iloc[0]
        subject = "Follow-up on Your Recent Appointment"
        result = send_email(patient_email, subject, message)
        
        return f"Follow-up sent to patient {patient_id}. {result}"
    except Exception as e:
        return f"Error sending follow-up: {str(e)}"

def send_intake_form(patient_id: str) -> str:
    """Send intake form via email."""
    try:
        patients_df = pd.read_csv("data/patients.csv")
        patient = patients_df[patients_df['patient_id'] == patient_id]
        if patient.empty:
            return f"Patient with ID {patient_id} not found."
        
        with open(EMAIL_TEMPLATES_FILE, 'r') as f:
            templates = json.load(f)
        
        template = templates.get('intake', 'Please fill out the intake form at https://example.com/intake.')
        message = template
        
        patient_email = patient['email'].iloc[0]
        subject = "Patient Intake Form"
        result = send_email(patient_email, subject, message)
        
        return f"Intake form sent to patient {patient_id}. {result}"
    except Exception as e:
        return f"Error sending intake form: {str(e)}"