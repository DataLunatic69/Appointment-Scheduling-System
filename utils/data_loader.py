import pandas as pd
import os
from typing import Dict, Any, List, Optional
from config import PATIENTS_FILE, APPOINTMENTS_FILE, DOCTOR_SCHEDULE_FILE, INSURANCE_FILE

def load_patients() -> pd.DataFrame:
    """Load patients data from CSV file."""
    try:
        if not os.path.exists(PATIENTS_FILE):
            # Create empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'patient_id', 'first_name', 'last_name', 'date_of_birth',
                'phone', 'email', 'insurance_provider', 'insurance_id',
                'primary_doctor', 'created_date'
            ])
        return pd.read_csv(PATIENTS_FILE)
    except Exception as e:
        print(f"Error loading patients data: {e}")
        return pd.DataFrame()

def load_appointments() -> pd.DataFrame:
    """Load appointments data from Excel file."""
    try:
        if not os.path.exists(APPOINTMENTS_FILE):
            # Create empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'appointment_id', 'patient_id', 'doctor_id', 'datetime',
                'status', 'notes'
            ])
        return pd.read_excel(APPOINTMENTS_FILE, sheet_name='Appointments')
    except Exception as e:
        print(f"Error loading appointments data: {e}")
        return pd.DataFrame()

def load_doctors() -> pd.DataFrame:
    """Load doctors data from Excel file."""
    try:
        if not os.path.exists(APPOINTMENTS_FILE):
            # Create empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'doctor_id', 'name', 'specialization', 'contact_info'
            ])
        return pd.read_excel(APPOINTMENTS_FILE, sheet_name='Doctors')
    except Exception as e:
        print(f"Error loading doctors data: {e}")
        return pd.DataFrame()

def load_doctor_schedules() -> pd.DataFrame:
    """Load doctor schedules from Excel file."""
    try:
        if not os.path.exists(DOCTOR_SCHEDULE_FILE):
            # Create empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'doctor_id', 'date', 'time_slots'
            ])
        return pd.read_excel(DOCTOR_SCHEDULE_FILE)
    except Exception as e:
        print(f"Error loading doctor schedules: {e}")
        return pd.DataFrame()

def load_insurance_data() -> Dict[str, pd.DataFrame]:
    """Load insurance data from Excel file."""
    try:
        if not os.path.exists(INSURANCE_FILE):
            # Return empty DataFrames for both sheets
            return {
                'Plans': pd.DataFrame(columns=[
                    'insurance_id', 'provider_name', 'plan_name', 'coverage_details'
                ]),
                'Verification': pd.DataFrame(columns=[
                    'patient_id', 'verification_status', 'last_verified', 'copay_amount'
                ])
            }
        
        return {
            'Plans': pd.read_excel(INSURANCE_FILE, sheet_name='Plans'),
            'Verification': pd.read_excel(INSURANCE_FILE, sheet_name='Verification')
        }
    except Exception as e:
        print(f"Error loading insurance data: {e}")
        return {
            'Plans': pd.DataFrame(),
            'Verification': pd.DataFrame()
        }

def get_patient_by_id(patient_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific patient by ID."""
    patients_df = load_patients()
    patient = patients_df[patients_df['patient_id'] == patient_id]
    if patient.empty:
        return None
    return patient.iloc[0].to_dict()

def get_doctor_by_id(doctor_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific doctor by ID."""
    doctors_df = load_doctors()
    doctor = doctors_df[doctors_df['doctor_id'] == doctor_id]
    if doctor.empty:
        return None
    return doctor.iloc[0].to_dict()

def get_appointment_by_id(appointment_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific appointment by ID."""
    appointments_df = load_appointments()
    appointment = appointments_df[appointments_df['appointment_id'] == appointment_id]
    if appointment.empty:
        return None
    return appointment.iloc[0].to_dict()

def save_patients(patients_df: pd.DataFrame) -> bool:
    """Save patients data to CSV file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(PATIENTS_FILE), exist_ok=True)
        patients_df.to_csv(PATIENTS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving patients data: {e}")
        return False

def save_appointments(appointments_df: pd.DataFrame) -> bool:
    """Save appointments data to Excel file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(APPOINTMENTS_FILE), exist_ok=True)
        with pd.ExcelWriter(APPOINTMENTS_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            appointments_df.to_excel(writer, sheet_name='Appointments', index=False)
        return True
    except Exception as e:
        print(f"Error saving appointments data: {e}")
        return False

def save_doctor_schedules(schedules_df: pd.DataFrame) -> bool:
    """Save doctor schedules to Excel file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(DOCTOR_SCHEDULE_FILE), exist_ok=True)
        schedules_df.to_excel(DOCTOR_SCHEDULE_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving doctor schedules: {e}")
        return False

def save_insurance_data(plans_df: pd.DataFrame, verification_df: pd.DataFrame) -> bool:
    """Save insurance data to Excel file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(INSURANCE_FILE), exist_ok=True)
        with pd.ExcelWriter(INSURANCE_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            plans_df.to_excel(writer, sheet_name='Plans', index=False)
            verification_df.to_excel(writer, sheet_name='Verification', index=False)
        return True
    except Exception as e:
        print(f"Error saving insurance data: {e}")
        return False