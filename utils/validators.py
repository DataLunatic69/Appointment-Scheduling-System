import re
from datetime import datetime
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    return bool(re.match(pattern, phone))

def validate_date(date_string: str, date_format: str = '%Y-%m-%d') -> bool:
    """Validate date format."""
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def validate_time(time_string: str) -> bool:
    """Validate time format (HH:MM)."""
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_string))

def validate_datetime(datetime_string: str, datetime_format: str = '%Y-%m-%d %H:%M') -> bool:
    """Validate datetime format."""
    try:
        datetime.strptime(datetime_string, datetime_format)
        return True
    except ValueError:
        return False

def validate_patient_id(patient_id: str, patients_df) -> bool:
    """Validate if patient ID exists."""
    return patient_id in patients_df['patient_id'].values

def validate_doctor_id(doctor_id: str, doctors_df) -> bool:
    """Validate if doctor ID exists."""
    return doctor_id in doctors_df['doctor_id'].values

def validate_appointment_id(appointment_id: str, appointments_df) -> bool:
    """Validate if appointment ID exists."""
    return appointment_id in appointments_df['appointment_id'].values

def validate_time_slot(doctor_id: str, date: str, time: str, schedules_df) -> bool:
    """Validate if a time slot is available for a doctor."""
    try:
        # Get doctor's schedule for the date
        doctor_schedule = schedules_df[
            (schedules_df['doctor_id'] == doctor_id) & 
            (schedules_df['date'] == date)
        ]
        
        if doctor_schedule.empty:
            return False
        
        # Check if time is in available time slots
        time_slots = doctor_schedule['time_slots'].iloc[0].split(',')
        return time in time_slots
    except Exception:
        return False

def validate_required_fields(data: dict, required_fields: list) -> tuple:
    """Validate that all required fields are present in the data."""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "All required fields are present"