import pandas as pd
from datetime import datetime, date
from typing import Dict, Any, List
import uuid
from langchain_core.tools import tool
from config import APPOINTMENTS_FILE, DOCTOR_SCHEDULE_FILE
from utils.logging_utils import logger, log_tool_execution
from utils.data_loader import load_appointments, load_doctors, load_doctor_schedules, save_appointments, load_patients
from utils.validators import validate_patient_id, validate_doctor_id, validate_appointment_id, validate_time_slot, validate_datetime, validate_date

@tool
def get_doctor_schedule(doctor_id: str, schedule_date: str) -> str:
    """Retrieve doctor's availability from XLSX. Use this when you need to check a doctor's schedule."""
    try:
        logger.info(f"Getting schedule for doctor {doctor_id} on {schedule_date}")
        
        # Validate inputs
        if not doctor_id or not isinstance(doctor_id, str):
            return "Doctor ID is required and must be a string."
        
        if not schedule_date or not isinstance(schedule_date, str):
            return "Schedule date is required and must be a string."
        
        # Validate date format
        if not validate_date(schedule_date):
            return "Invalid date format. Please use YYYY-MM-DD format."
        
        schedules_df = load_doctor_schedules()
        doctors_df = load_doctors()
        
        # Check if doctor exists
        if not validate_doctor_id(doctor_id, doctors_df):
            return f"Doctor with ID {doctor_id} not found."
        
        # Filter by doctor_id and date
        schedule = schedules_df[(schedules_df['doctor_id'] == doctor_id) & (schedules_df['date'] == schedule_date)]
        
        if schedule.empty:
            result = f"No schedule found for doctor {doctor_id} on {schedule_date}."
        else:
            result = schedule.to_json(orient='records', indent=2)
        
        # Log the tool execution
        log_tool_execution("get_doctor_schedule", {"doctor_id": doctor_id, "schedule_date": schedule_date}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error retrieving doctor schedule: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def check_availability(doctor_id: str, datetime_str: str) -> str:
    """Check if a time slot is available. Use this when you need to verify if a doctor is available at a specific time."""
    try:
        logger.info(f"Checking availability for doctor {doctor_id} at {datetime_str}")
        
        # Validate inputs
        if not doctor_id or not isinstance(doctor_id, str):
            return "Doctor ID is required and must be a string."
        
        if not datetime_str or not isinstance(datetime_str, str):
            return "Datetime is required and must be a string."
        
        # Validate datetime format
        if not validate_datetime(datetime_str):
            return "Invalid datetime format. Please use YYYY-MM-DD HH:MM format."
        
        # Parse datetime
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        
        # Read doctor's availability
        schedules_df = load_doctor_schedules()
        doctors_df = load_doctors()
        
        # Check if doctor exists
        if not validate_doctor_id(doctor_id, doctors_df):
            return f"Doctor with ID {doctor_id} not found."
        
        doctor_availability = schedules_df[(schedules_df['doctor_id'] == doctor_id) & (schedules_df['date'] == date_str)]
        
        if doctor_availability.empty:
            result = f"Doctor {doctor_id} is not available on {date_str}."
        else:
            # Check if time slot is in available time slots
            available_slots = doctor_availability['time_slots'].iloc[0].split(',')
            if time_str in available_slots:
                result = f"Doctor {doctor_id} is available at {datetime_str}."
            else:
                result = f"Doctor {doctor_id} is not available at {datetime_str}."
        
        # Log the tool execution
        log_tool_execution("check_availability", {"doctor_id": doctor_id, "datetime": datetime_str}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error checking availability: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def schedule_appointment(patient_id: str, doctor_id: str, datetime_str: str) -> str:
    """Book an appointment and update appointments.xlsx. Use this when you need to schedule a new appointment."""
    try:
        logger.info(f"Scheduling appointment for patient {patient_id} with doctor {doctor_id} at {datetime_str}")
        
        # Validate inputs
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        if not doctor_id or not isinstance(doctor_id, str):
            return "Doctor ID is required and must be a string."
        
        if not datetime_str or not isinstance(datetime_str, str):
            return "Datetime is required and must be a string."
        
        # Validate datetime format
        if not validate_datetime(datetime_str):
            return "Invalid datetime format. Please use YYYY-MM-DD HH:MM format."
        
        # Check if patient exists
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        # Check if doctor exists
        doctors_df = load_doctors()
        if not validate_doctor_id(doctor_id, doctors_df):
            return f"Doctor with ID {doctor_id} not found."
        
        # Check availability
        availability_result = check_availability(doctor_id, datetime_str)
        if "not available" in availability_result:
            return availability_result
        
        # Create new appointment
        appointments_df = load_appointments()
        new_appointment = {
            'appointment_id': str(uuid.uuid4())[:8],
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'datetime': datetime_str,
            'status': 'scheduled',
            'notes': ''
        }
        
        new_row = pd.DataFrame([new_appointment])
        appointments_df = pd.concat([appointments_df, new_row], ignore_index=True)
        
        # Save the updated data
        save_appointments(appointments_df)
        
        result = f"Appointment scheduled successfully. Appointment ID: {new_appointment['appointment_id']}"
        
        # Log the tool execution
        log_tool_execution("schedule_appointment", {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "datetime": datetime_str
        }, result)
        
        return result
    except Exception as e:
        error_msg = f"Error scheduling appointment: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def reschedule_appointment(appointment_id: str, new_datetime: str) -> str:
    """Change appointment time. Use this when you need to reschedule an existing appointment."""
    try:
        logger.info(f"Rescheduling appointment {appointment_id} to {new_datetime}")
        
        # Validate inputs
        if not appointment_id or not isinstance(appointment_id, str):
            return "Appointment ID is required and must be a string."
        
        if not new_datetime or not isinstance(new_datetime, str):
            return "New datetime is required and must be a string."
        
        # Validate datetime format
        if not validate_datetime(new_datetime):
            return "Invalid datetime format. Please use YYYY-MM-DD HH:MM format."
        
        appointments_df = load_appointments()
        
        # Check if appointment exists
        if not validate_appointment_id(appointment_id, appointments_df):
            return f"Appointment with ID {appointment_id} not found."
        
        idx = appointments_df[appointments_df['appointment_id'] == appointment_id].index[0]
        doctor_id = appointments_df.at[idx, 'doctor_id']
        
        # Check new availability
        availability_result = check_availability(doctor_id, new_datetime)
        if "not available" in availability_result:
            return availability_result
        
        # Update appointment
        appointments_df.at[idx, 'datetime'] = new_datetime
        appointments_df.at[idx, 'status'] = 'rescheduled'
        
        # Save the updated data
        save_appointments(appointments_df)
        
        result = f"Appointment {appointment_id} rescheduled to {new_datetime}."
        
        # Log the tool execution
        log_tool_execution("reschedule_appointment", {
            "appointment_id": appointment_id,
            "new_datetime": new_datetime
        }, result)
        
        return result
    except Exception as e:
        error_msg = f"Error rescheduling appointment: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def cancel_appointment(appointment_id: str) -> str:
    """Cancel an appointment. Use this when you need to cancel an existing appointment."""
    try:
        logger.info(f"Canceling appointment {appointment_id}")
        
        # Validate input
        if not appointment_id or not isinstance(appointment_id, str):
            return "Appointment ID is required and must be a string."
        
        appointments_df = load_appointments()
        
        # Check if appointment exists
        if not validate_appointment_id(appointment_id, appointments_df):
            return f"Appointment with ID {appointment_id} not found."
        
        idx = appointments_df[appointments_df['appointment_id'] == appointment_id].index[0]
        appointments_df.at[idx, 'status'] = 'cancelled'
        
        # Save the updated data
        save_appointments(appointments_df)
        
        result = f"Appointment {appointment_id} cancelled."
        
        # Log the tool execution
        log_tool_execution("cancel_appointment", {"appointment_id": appointment_id}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error cancelling appointment: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def get_appointments(date_str: str) -> str:
    """Get all appointments for a date. Use this when you need to view appointments for a specific date."""
    try:
        logger.info(f"Getting appointments for date: {date_str}")
        
        # Validate input
        if not date_str or not isinstance(date_str, str):
            return "Date is required and must be a string."
        
        # Validate date format
        if not validate_date(date_str):
            return "Invalid date format. Please use YYYY-MM-DD format."
        
        appointments_df = load_appointments()
        
        # Convert datetime column to date for comparison
        appointments_df['date'] = pd.to_datetime(appointments_df['datetime']).dt.date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        daily_appointments = appointments_df[appointments_df['date'] == target_date]
        
        if daily_appointments.empty:
            result = f"No appointments found for {date_str}."
        else:
            result = daily_appointments.to_json(orient='records', indent=2)
        
        # Log the tool execution
        log_tool_execution("get_appointments", {"date": date_str}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error retrieving appointments: {str(e)}"
        logger.error(error_msg)
        return error_msg