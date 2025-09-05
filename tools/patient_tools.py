import pandas as pd
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from langchain_core.tools import tool
from config import PATIENTS_FILE
from utils.logging_utils import logger, log_tool_execution
from utils.data_loader import load_patients, save_patients
from utils.validators import validate_patient_id, validate_required_fields

@tool
def get_patient_info(patient_id: str) -> str:
    """Retrieve patient details from CSV. Use this when you need to get information about a specific patient."""
    try:
        logger.info(f"Getting patient info for ID: {patient_id}")
        
        # Validate input
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        patients_df = load_patients()
        
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        patient = patients_df[patients_df['patient_id'] == patient_id]
        result = patient.to_json(orient='records', indent=2)
        
        # Log the tool execution
        log_tool_execution("get_patient_info", {"patient_id": patient_id}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error retrieving patient information: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def update_patient_info(patient_id: str, updates: Dict[str, Any]) -> str:
    """Update patient information in CSV. Use this when you need to modify a patient's details."""
    try:
        logger.info(f"Updating patient info for ID: {patient_id} with updates: {updates}")
        
        # Validate inputs
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        if not updates or not isinstance(updates, dict):
            return "Updates are required and must be a dictionary."
        
        patients_df = load_patients()
        
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        # Validate that updates contain valid fields
        valid_fields = patients_df.columns.tolist()
        invalid_fields = [field for field in updates.keys() if field not in valid_fields]
        
        if invalid_fields:
            return f"Invalid field(s) in updates: {', '.join(invalid_fields)}. Valid fields are: {', '.join(valid_fields)}"
        
        # Update the patient record
        idx = patients_df[patients_df['patient_id'] == patient_id].index[0]
        for key, value in updates.items():
            patients_df.at[idx, key] = value
        
        # Save the updated data
        save_patients(patients_df)
        
        result = f"Patient {patient_id} information updated successfully."
        
        # Log the tool execution
        log_tool_execution("update_patient_info", {"patient_id": patient_id, "updates": updates}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error updating patient information: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def create_patient(patient_data: Dict[str, Any]) -> str:
    """Add a new patient to CSV. Use this when you need to create a new patient record."""
    try:
        logger.info(f"Creating new patient with data: {patient_data}")
        
        # Validate input
        if not patient_data or not isinstance(patient_data, dict):
            return "Patient data is required and must be a dictionary."
        
        # Check required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 'email']
        is_valid, message = validate_required_fields(patient_data, required_fields)
        
        if not is_valid:
            return message
        
        patients_df = load_patients()
        
        # Generate a unique patient ID if not provided
        if 'patient_id' not in patient_data:
            patient_data['patient_id'] = str(uuid.uuid4())[:8]
        
        # Set created date if not provided
        if 'created_date' not in patient_data:
            patient_data['created_date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Add the new patient
        new_row = pd.DataFrame([patient_data])
        patients_df = pd.concat([patients_df, new_row], ignore_index=True)
        
        # Save the updated data
        save_patients(patients_df)
        
        result = f"Patient created successfully with ID: {patient_data['patient_id']}"
        
        # Log the tool execution
        log_tool_execution("create_patient", {"patient_data": patient_data}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error creating patient: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def search_patients(query: str) -> str:
    """Search patients by name or other criteria. Use this when you need to find patients based on search terms."""
    try:
        logger.info(f"Searching patients with query: {query}")
        
        # Validate input
        if not query or not isinstance(query, str):
            return "Search query is required and must be a string."
        
        patients_df = load_patients()
        
        # Convert all columns to string for searching
        patients_str = patients_df.astype(str)
        
        # Search across all columns
        mask = patients_str.apply(lambda row: row.str.contains(query, case=False).any(), axis=1)
        results = patients_df[mask]
        
        if results.empty:
            result = "No patients found matching the query."
        else:
            result = results.to_json(orient='records', indent=2)
        
        # Log the tool execution
        log_tool_execution("search_patients", {"query": query}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error searching patients: {str(e)}"
        logger.error(error_msg)
        return error_msg