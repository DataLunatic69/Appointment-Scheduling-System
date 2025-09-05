import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any
from langchain_core.tools import tool
from config import EMAIL_TEMPLATES_FILE
from utils.logging_utils import logger, log_tool_execution
from utils.data_loader import load_patients, load_appointments, load_doctors
from utils.email_utils import send_email, create_email_template
from utils.validators import validate_patient_id, validate_appointment_id

@tool
def send_appointment_reminder(patient_id: str, appointment_id: str) -> str:
    """Send appointment reminder via email. Use this when you need to send a reminder for an upcoming appointment."""
    try:
        logger.info(f"Sending appointment reminder to patient {patient_id} for appointment {appointment_id}")
        
        # Validate inputs
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        if not appointment_id or not isinstance(appointment_id, str):
            return "Appointment ID is required and must be a string."
        
        # Get patient info
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        patient = patients_df[patients_df['patient_id'] == patient_id].iloc[0]
        
        # Get appointment info
        appointments_df = load_appointments()
        if not validate_appointment_id(appointment_id, appointments_df):
            return f"Appointment with ID {appointment_id} not found."
        
        appointment = appointments_df[appointments_df['appointment_id'] == appointment_id].iloc[0]
        
        # Get doctor info
        doctors_df = load_doctors()
        doctor_id = appointment['doctor_id']
        doctor = doctors_df[doctors_df['doctor_id'] == doctor_id].iloc[0] if doctor_id in doctors_df['doctor_id'].values else None
        doctor_name = doctor['name'] if doctor is not None else "the doctor"
        
        # Create and send email
        variables = {
            "patient_name": f"{patient['first_name']} {patient['last_name']}",
            "doctor": doctor_name,
            "datetime": appointment['datetime']
        }
        
        message = create_email_template("appointment_reminder", variables)
        subject = "Appointment Reminder"
        
        email_result = send_email(patient['email'], subject, message)
        
        if email_result["success"]:
            result = f"Appointment reminder sent to patient {patient_id} for appointment {appointment_id}."
        else:
            result = f"Failed to send appointment reminder: {email_result['message']}"
        
        # Log the tool execution
        log_tool_execution("send_appointment_reminder", {
            "patient_id": patient_id,
            "appointment_id": appointment_id
        }, result)
        
        return result
    except Exception as e:
        error_msg = f"Error sending appointment reminder: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def send_followup(patient_id: str, appointment_id: str) -> str:
    """Send follow-up message via email. Use this when you need to send a follow-up after an appointment."""
    try:
        logger.info(f"Sending follow-up to patient {patient_id} for appointment {appointment_id}")
        
        # Validate inputs
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        if not appointment_id or not isinstance(appointment_id, str):
            return "Appointment ID is required and must be a string."
        
        # Get patient info
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        patient = patients_df[patients_df['patient_id'] == patient_id].iloc[0]
        
        # Get appointment info if available
        doctors_df = load_doctors()
        doctor_name = "the doctor"
        
        appointments_df = load_appointments()
        if validate_appointment_id(appointment_id, appointments_df):
            appointment = appointments_df[appointments_df['appointment_id'] == appointment_id].iloc[0]
            doctor_id = appointment['doctor_id']
            doctor = doctors_df[doctors_df['doctor_id'] == doctor_id].iloc[0] if doctor_id in doctors_df['doctor_id'].values else None
            doctor_name = doctor['name'] if doctor is not None else "the doctor"
        
        # Create and send email
        variables = {
            "patient_name": f"{patient['first_name']} {patient['last_name']}",
            "doctor": doctor_name
        }
        
        message = create_email_template("follow_up", variables)
        subject = "Follow-up on Your Recent Appointment"
        
        email_result = send_email(patient['email'], subject, message)
        
        if email_result["success"]:
            result = f"Follow-up sent to patient {patient_id}."
        else:
            result = f"Failed to send follow-up: {email_result['message']}"
        
        # Log the tool execution
        log_tool_execution("send_followup", {
            "patient_id": patient_id,
            "appointment_id": appointment_id
        }, result)
        
        return result
    except Exception as e:
        error_msg = f"Error sending follow-up: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def send_intake_form(patient_id: str) -> str:
    """Send intake form via email. Use this when you need to send an intake form to a patient."""
    try:
        logger.info(f"Sending intake form to patient {patient_id}")
        
        # Validate input
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        # Get patient info
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        patient = patients_df[patients_df['patient_id'] == patient_id].iloc[0]
        
        # Create and send email
        variables = {
            "patient_name": f"{patient['first_name']} {patient['last_name']}"
        }
        
        message = create_email_template("intake", variables)
        subject = "Patient Intake Form"
        
        email_result = send_email(patient['email'], subject, message)
        
        if email_result["success"]:
            result = f"Intake form sent to patient {patient_id}."
        else:
            result = f"Failed to send intake form: {email_result['message']}"
        
        # Log the tool execution
        log_tool_execution("send_intake_form", {"patient_id": patient_id}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error sending intake form: {str(e)}"
        logger.error(error_msg)
        return error_msg