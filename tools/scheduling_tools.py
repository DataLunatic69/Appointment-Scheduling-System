import pandas as pd
from datetime import datetime, date
from typing import Dict, Any, List
import uuid

APPOINTMENTS_FILE = "data/appointments.xlsx"
DOCTOR_SCHEDULE_FILE = "data/doctor_schedules.xlsx"

def get_doctor_schedule(doctor_id: str, schedule_date: str) -> str:
    """Retrieve doctor's availability from XLSX."""
    try:
        df = pd.read_excel(DOCTOR_SCHEDULE_FILE, sheet_name='Availability')
        # Filter by doctor_id and date
        schedule = df[(df['doctor_id'] == doctor_id) & (df['date'] == schedule_date)]
        if schedule.empty:
            return f"No schedule found for doctor {doctor_id} on {schedule_date}."
        return schedule.to_json(orient='records', indent=2)
    except Exception as e:
        return f"Error retrieving doctor schedule: {str(e)}"

def check_availability(doctor_id: str, datetime_str: str) -> str:
    """Check if a time slot is available."""
    try:
        # Parse datetime
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        
        # Read doctor's availability
        availability_df = pd.read_excel(DOCTOR_SCHEDULE_FILE, sheet_name='Availability')
        doctor_availability = availability_df[(availability_df['doctor_id'] == doctor_id) & (availability_df['date'] == date_str)]
        if doctor_availability.empty:
            return f"Doctor {doctor_id} is not available on {date_str}."
        
        # Check if time slot is in available time slots
        available_slots = doctor_availability['time_slots'].iloc[0].split(',')
        if time_str in available_slots:
            return f"Doctor {doctor_id} is available at {datetime_str}."
        else:
            return f"Doctor {doctor_id} is not available at {datetime_str}."
    except Exception as e:
        return f"Error checking availability: {str(e)}"

def schedule_appointment(patient_id: str, doctor_id: str, datetime_str: str) -> str:
    """Book an appointment and update appointments.xlsx."""
    try:
        # Check if patient exists
        patients_df = pd.read_csv("data/patients.csv")
        if patient_id not in patients_df['patient_id'].values:
            return f"Patient with ID {patient_id} not found."
        
        # Check if doctor exists
        doctors_df = pd.read_excel(APPOINTMENTS_FILE, sheet_name='Doctors')
        if doctor_id not in doctors_df['doctor_id'].values:
            return f"Doctor with ID {doctor_id} not found."
        
        # Check availability
        availability_result = check_availability(doctor_id, datetime_str)
        if "not available" in availability_result:
            return availability_result
        
        # Create new appointment
        appointments_df = pd.read_excel(APPOINTMENTS_FILE, sheet_name='Appointments')
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
        
        # Save back to Excel
        with pd.ExcelWriter(APPOINTMENTS_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            appointments_df.to_excel(writer, sheet_name='Appointments', index=False)
        
        return f"Appointment scheduled successfully. Appointment ID: {new_appointment['appointment_id']}"
    except Exception as e:
        return f"Error scheduling appointment: {str(e)}"

def reschedule_appointment(appointment_id: str, new_datetime: str) -> str:
    """Change appointment time."""
    try:
        appointments_df = pd.read_excel(APPOINTMENTS_FILE, sheet_name='Appointments')
        if appointment_id not in appointments_df['appointment_id'].values:
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
        
        # Save back to Excel
        with pd.ExcelWriter(APPOINTMENTS_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            appointments_df.to_excel(writer, sheet_name='Appointments', index=False)
        
        return f"Appointment {appointment_id} rescheduled to {new_datetime}."
    except Exception as e:
        return f"Error rescheduling appointment: {str(e)}"

def cancel_appointment(appointment_id: str) -> str:
    """Cancel an appointment."""
    try:
        appointments_df = pd.read_excel(APPOINTMENTS_FILE, sheet_name='Appointments')
        if appointment_id not in appointments_df['appointment_id'].values:
            return f"Appointment with ID {appointment_id} not found."
        
        idx = appointments_df[appointments_df['appointment_id'] == appointment_id].index[0]
        appointments_df.at[idx, 'status'] = 'cancelled'
        
        with pd.ExcelWriter(APPOINTMENTS_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            appointments_df.to_excel(writer, sheet_name='Appointments', index=False)
        
        return f"Appointment {appointment_id} cancelled."
    except Exception as e:
        return f"Error cancelling appointment: {str(e)}"

def get_appointments(date_str: str) -> str:
    """Get all appointments for a date."""
    try:
        appointments_df = pd.read_excel(APPOINTMENTS_FILE, sheet_name='Appointments')
        appointments_df['date'] = pd.to_datetime(appointments_df['datetime']).dt.date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        daily_appointments = appointments_df[appointments_df['date'] == target_date]
        if daily_appointments.empty:
            return f"No appointments found for {date_str}."
        return daily_appointments.to_json(orient='records', indent=2)
    except Exception as e:
        return f"Error retrieving appointments: {str(e)}"