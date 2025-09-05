import pandas as pd
import os
import json
from typing import Dict, Any, List
from config import PATIENTS_FILE, APPOINTMENTS_FILE, DOCTOR_SCHEDULE_FILE, INSURANCE_FILE

def ensure_directory_exists(file_path: str) -> None:
    """Ensure the directory for a file path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def save_to_csv(df: pd.DataFrame, file_path: str) -> bool:
    """Save DataFrame to CSV file."""
    try:
        ensure_directory_exists(file_path)
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving to CSV {file_path}: {e}")
        return False

def save_to_excel(df: pd.DataFrame, file_path: str, sheet_name: str = 'Sheet1') -> bool:
    """Save DataFrame to Excel file."""
    try:
        ensure_directory_exists(file_path)
        
        # If file exists, we need to handle it differently to preserve other sheets
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True
    except Exception as e:
        print(f"Error saving to Excel {file_path}: {e}")
        return False

def save_patients(patients_df: pd.DataFrame) -> bool:
    """Save patients data to CSV file."""
    return save_to_csv(patients_df, PATIENTS_FILE)

def save_appointments(appointments_df: pd.DataFrame) -> bool:
    """Save appointments data to Excel file."""
    return save_to_excel(appointments_df, APPOINTMENTS_FILE, 'Appointments')

def save_doctors(doctors_df: pd.DataFrame) -> bool:
    """Save doctors data to Excel file."""
    return save_to_excel(doctors_df, APPOINTMENTS_FILE, 'Doctors')

def save_doctor_schedules(schedules_df: pd.DataFrame) -> bool:
    """Save doctor schedules to Excel file."""
    return save_to_excel(schedules_df, DOCTOR_SCHEDULE_FILE)

def save_insurance_data(plans_df: pd.DataFrame, verification_df: pd.DataFrame) -> bool:
    """Save insurance data to Excel file."""
    try:
        ensure_directory_exists(INSURANCE_FILE)
        
        with pd.ExcelWriter(INSURANCE_FILE, engine='openpyxl') as writer:
            plans_df.to_excel(writer, sheet_name='Plans', index=False)
            verification_df.to_excel(writer, sheet_name='Verification', index=False)
        
        return True
    except Exception as e:
        print(f"Error saving insurance data: {e}")
        return False

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    try:
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to a JSON file."""
    try:
        ensure_directory_exists(file_path)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False