import pandas as pd
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

PATIENTS_FILE = "data/patients.csv"

def get_patient_info(patient_id: str) -> str:
    """Retrieve patient details from CSV."""
    try:
        df = pd.read_csv(PATIENTS_FILE)
        patient = df[df['patient_id'] == patient_id]
        if patient.empty:
            return f"Patient with ID {patient_id} not found."
        return patient.to_json(orient='records', indent=2)
    except Exception as e:
        return f"Error retrieving patient information: {str(e)}"

def update_patient_info(patient_id: str, updates: Dict[str, Any]) -> str:
    """Update patient information in CSV."""
    try:
        df = pd.read_csv(PATIENTS_FILE)
        if patient_id not in df['patient_id'].values:
            return f"Patient with ID {patient_id} not found."
        
        idx = df[df['patient_id'] == patient_id].index[0]
        for key, value in updates.items():
            if key in df.columns:
                df.at[idx, key] = value
        
        df.to_csv(PATIENTS_FILE, index=False)
        return f"Patient {patient_id} information updated successfully."
    except Exception as e:
        return f"Error updating patient information: {str(e)}"

def create_patient(patient_data: Dict[str, Any]) -> str:
    """Add a new patient to CSV."""
    try:
        df = pd.read_csv(PATIENTS_FILE)
        # Generate a unique patient ID if not provided
        if 'patient_id' not in patient_data:
            patient_data['patient_id'] = str(uuid.uuid4())[:8]
        # Set created date if not provided
        if 'created_date' not in patient_data:
            patient_data['created_date'] = datetime.now().strftime("%Y-%m-%d")
        
        new_row = pd.DataFrame([patient_data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(PATIENTS_FILE, index=False)
        return f"Patient created successfully with ID: {patient_data['patient_id']}"
    except Exception as e:
        return f"Error creating patient: {str(e)}"

def search_patients(query: str) -> str:
    """Search patients by name or other criteria."""
    try:
        df = pd.read_csv(PATIENTS_FILE)
        # Convert all columns to string for searching
        df_str = df.astype(str)
        # Search across all columns
        mask = df_str.apply(lambda row: row.str.contains(query, case=False).any(), axis=1)
        results = df[mask]
        if results.empty:
            return "No patients found matching the query."
        return results.to_json(orient='records', indent=2)
    except Exception as e:
        return f"Error searching patients: {str(e)}"