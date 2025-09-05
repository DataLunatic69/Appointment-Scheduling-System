import pandas as pd
from typing import Dict, Any

INSURANCE_FILE = "data/insurance_plans.xlsx"

def verify_insurance(patient_id: str, plan_details: Dict[str, Any]) -> str:
    """Verify insurance coverage."""
    try:
        # Check if patient exists
        patients_df = pd.read_csv("data/patients.csv")
        if patient_id not in patients_df['patient_id'].values:
            return f"Patient with ID {patient_id} not found."
        
        # Read insurance plans
        verification_df = pd.read_excel(INSURANCE_FILE, sheet_name='Verification')
        plans_df = pd.read_excel(INSURANCE_FILE, sheet_name='Plans')
        
        # Check if patient already has verification record
        if patient_id in verification_df['patient_id'].values:
            idx = verification_df[verification_df['patient_id'] == patient_id].index[0]
            verification_df.at[idx, 'verification_status'] = 'verified'
            verification_df.at[idx, 'last_verified'] = pd.Timestamp.now().strftime("%Y-%m-%d")
        else:
            new_verification = {
                'patient_id': patient_id,
                'verification_status': 'verified',
                'last_verified': pd.Timestamp.now().strftime("%Y-%m-%d"),
                'copay_amount': plan_details.get('copay', 0)
            }
            verification_df = pd.concat([verification_df, pd.DataFrame([new_verification])], ignore_index=True)
        
        # Save back to Excel
        with pd.ExcelWriter(INSURANCE_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            verification_df.to_excel(writer, sheet_name='Verification', index=False)
        
        return f"Insurance verified for patient {patient_id}."
    except Exception as e:
        return f"Error verifying insurance: {str(e)}"

def check_coverage(patient_id: str, procedure_code: str) -> str:
    """Check if a procedure is covered."""
    try:
        verification_df = pd.read_excel(INSURANCE_FILE, sheet_name='Verification')
        if patient_id not in verification_df['patient_id'].values:
            return f"No insurance verification found for patient {patient_id}. Please verify insurance first."
        
        # Simulate coverage check - in real scenario, we might have a coverage table
        coverage_status = "covered"  # Assume covered for demo
        return f"Procedure {procedure_code} is {coverage_status} for patient {patient_id}."
    except Exception as e:
        return f"Error checking coverage: {str(e)}"

def get_copay_info(patient_id: str) -> str:
    """Retrieve copayment information."""
    try:
        verification_df = pd.read_excel(INSURANCE_FILE, sheet_name='Verification')
        if patient_id not in verification_df['patient_id'].values:
            return f"No insurance information found for patient {patient_id}."
        
        copay = verification_df[verification_df['patient_id'] == patient_id]['copay_amount'].iloc[0]
        return f"Copay amount for patient {patient_id} is ${copay}."
    except Exception as e:
        return f"Error retrieving copay info: {str(e)}"