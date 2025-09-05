import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any

EMAIL_TEMPLATES_FILE = "data/templates/email_templates.json"

def send_appointment_reminder(patient_id: str, appointment_id: str) -> str:
    """Send appointment reminder (simulate)."""
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
        
        # Load email templates
        with open(EMAIL_TEMPLATES_FILE, 'r') as f:
            templates = json.load(f)
        
        template = templates.get('reminder', 'Your appointment is scheduled for {datetime}.')
        appointment_time = appointment['datetime'].iloc[0]
        message = template.format(datetime=appointment_time)
        
        # Simulate sending email (just log for now)
        print(f"Email sent to {patient['email'].iloc[0]}: {message}")
        return f"Reminder sent to patient {patient_id} for appointment {appointment_id}."
    except Exception as e:
        return f"Error sending reminder: {str(e)}"

def send_followup(patient_id: str, appointment_id: str) -> str:
    """Send follow-up message (simulate)."""
    try:
        patients_df = pd.read_csv("data/patients.csv")
        patient = patients_df[patients_df['patient_id'] == patient_id]
        if patient.empty:
            return f"Patient with ID {patient_id} not found."
        
        with open(EMAIL_TEMPLATES_FILE, 'r') as f:
            templates = json.load(f)
        
        template = templates.get('followup', 'Thank you for your appointment. How was your experience?')
        message = template
        
        print(f"Email sent to {patient['email'].iloc[0]}: {message}")
        return f"Follow-up sent to patient {patient_id}."
    except Exception as e:
        return f"Error sending follow-up: {str(e)}"

def send_intake_form(patient_id: str) -> str:
    """Send intake form (simulate)."""
    try:
        patients_df = pd.read_csv("data/patients.csv")
        patient = patients_df[patients_df['patient_id'] == patient_id]
        if patient.empty:
            return f"Patient with ID {patient_id} not found."
        
        with open(EMAIL_TEMPLATES_FILE, 'r') as f:
            templates = json.load(f)
        
        template = templates.get('intake', 'Please fill out the intake form at [link].')
        message = template
        
        print(f"Email sent to {patient['email'].iloc[0]}: {message}")
        return f"Intake form sent to patient {patient_id}."
    except Exception as e:
        return f"Error sending intake form: {str(e)}"