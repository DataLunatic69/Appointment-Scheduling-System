import pandas as pd
from datetime import datetime
from typing import Dict, Any
from langchain_core.tools import tool
from config import INSURANCE_FILE
from utils.logging_utils import logger, log_tool_execution
from utils.data_loader import load_insurance_data, save_insurance_data, load_patients
from utils.validators import validate_patient_id

@tool
def verify_insurance(patient_id: str, plan_details: Dict[str, Any]) -> str:
    """Verify insurance coverage. Use this when you need to verify a patient's insurance."""
    try:
        logger.info(f"Verifying insurance for patient {patient_id} with details: {plan_details}")
        
        # Validate inputs
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        if not plan_details or not isinstance(plan_details, dict):
            return "Plan details are required and must be a dictionary."
        
        # Check if patient exists
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        # Read insurance data
        insurance_data = load_insurance_data()
        verification_df = insurance_data['Verification']
        plans_df = insurance_data['Plans']
        
        # Check if patient already has verification record
        if patient_id in verification_df['patient_id'].values:
            idx = verification_df[verification_df['patient_id'] == patient_id].index[0]
            verification_df.at[idx, 'verification_status'] = 'verified'
            verification_df.at[idx, 'last_verified'] = datetime.now().strftime("%Y-%m-%d")
        else:
            new_verification = {
                'patient_id': patient_id,
                'verification_status': 'verified',
                'last_verified': datetime.now().strftime("%Y-%m-%d"),
                'copay_amount': plan_details.get('copay', 0)
            }
            verification_df = pd.concat([verification_df, pd.DataFrame([new_verification])], ignore_index=True)
        
        # Save the updated data
        save_insurance_data(plans_df, verification_df)
        
        result = f"Insurance verified for patient {patient_id}."
        
        # Log the tool execution
        log_tool_execution("verify_insurance", {
            "patient_id": patient_id,
            "plan_details": plan_details
        }, result)
        
        return result
    except Exception as e:
        error_msg = f"Error verifying insurance: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def check_coverage(patient_id: str, procedure_code: str) -> str:
    """Check if a procedure is covered. Use this when you need to check coverage for a specific procedure."""
    try:
        logger.info(f"Checking coverage for patient {patient_id}, procedure {procedure_code}")
        
        # Validate inputs
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        if not procedure_code or not isinstance(procedure_code, str):
            return "Procedure code is required and must be a string."
        
        # Check if patient exists
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        # Read insurance verification data
        insurance_data = load_insurance_data()
        verification_df = insurance_data['Verification']
        
        # Check if insurance is verified
        if patient_id not in verification_df['patient_id'].values:
            return f"No insurance verification found for patient {patient_id}. Please verify insurance first."
        
        # Simulate coverage check - in real scenario, we might have a coverage table
        # For demo purposes, we'll assume most procedures are covered
        coverage_status = "covered" if not procedure_code.startswith("EXCL") else "not covered"
        
        result = f"Procedure {procedure_code} is {coverage_status} for patient {patient_id}."
        
        # Log the tool execution
        log_tool_execution("check_coverage", {
            "patient_id": patient_id,
            "procedure_code": procedure_code
        }, result)
        
        return result
    except Exception as e:
        error_msg = f"Error checking coverage: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def get_copay_info(patient_id: str) -> str:
    """Retrieve copayment information. Use this when you need to get a patient's copay amount."""
    try:
        logger.info(f"Getting copay info for patient {patient_id}")
        
        # Validate input
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        # Check if patient exists
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        # Read insurance verification data
        insurance_data = load_insurance_data()
        verification_df = insurance_data['Verification']
        
        # Check if insurance information exists
        if patient_id not in verification_df['patient_id'].values:
            return f"No insurance information found for patient {patient_id}."
        
        copay = verification_df[verification_df['patient_id'] == patient_id]['copay_amount'].iloc[0]
        
        result = f"Copay amount for patient {patient_id} is ${copay}."
        
        # Log the tool execution
        log_tool_execution("get_copay_info", {"patient_id": patient_id}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error retrieving copay info: {str(e)}"
        logger.error(error_msg)
        return error_msg