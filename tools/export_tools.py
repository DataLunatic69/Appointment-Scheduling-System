import pandas as pd
from datetime import datetime, timedelta
import os
from langchain_core.tools import tool
from config import DATA_DIR
from utils.logging_utils import logger, log_tool_execution
from utils.data_loader import load_appointments, load_patients, load_doctors
from utils.file_operations import save_to_csv, ensure_directory_exists
from utils.validators import validate_date, validate_patient_id

@tool
def generate_daily_schedule(date_str: str) -> str:
    """Generate daily schedule report. Use this when you need to create a schedule report for a specific day."""
    try:
        logger.info(f"Generating daily schedule for {date_str}")
        
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
            # Merge with patient and doctor info
            patients_df = load_patients()
            doctors_df = load_doctors()
            
            daily_schedule = daily_appointments.merge(patients_df, on='patient_id', how='left')
            daily_schedule = daily_schedule.merge(doctors_df, on='doctor_id', how='left')
            
            # Save to CSV
            output_file = f"data/reports/daily_schedule_{date_str}.csv"
            ensure_directory_exists(output_file)
            
            save_to_csv(daily_schedule, output_file)
            result = f"Daily schedule report generated: {output_file}"
        
        # Log the tool execution
        log_tool_execution("generate_daily_schedule", {"date": date_str}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error generating daily schedule: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def generate_patient_report(patient_id: str) -> str:
    """Create patient history report. Use this when you need to generate a report for a specific patient."""
    try:
        logger.info(f"Generating patient report for {patient_id}")
        
        # Validate input
        if not patient_id or not isinstance(patient_id, str):
            return "Patient ID is required and must be a string."
        
        # Check if patient exists
        patients_df = load_patients()
        if not validate_patient_id(patient_id, patients_df):
            return f"Patient with ID {patient_id} not found."
        
        appointments_df = load_appointments()
        patient_appointments = appointments_df[appointments_df['patient_id'] == patient_id]
        
        if patient_appointments.empty:
            result = f"No appointments found for patient {patient_id}."
        else:
            # Merge with doctor info
            doctors_df = load_doctors()
            patient_report = patient_appointments.merge(doctors_df, on='doctor_id', how='left')
            
            # Save to CSV
            output_file = f"data/reports/patient_report_{patient_id}.csv"
            ensure_directory_exists(output_file)
            
            save_to_csv(patient_report, output_file)
            result = f"Patient report generated: {output_file}"
        
        # Log the tool execution
        log_tool_execution("generate_patient_report", {"patient_id": patient_id}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error generating patient report: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def export_appointments(date_range: str) -> str:
    """Export appointments for a period. Use this when you need to export appointments for a date range."""
    try:
        logger.info(f"Exporting appointments for date range: {date_range}")
        
        # Validate input
        if not date_range or not isinstance(date_range, str):
            return "Date range is required and must be a string."
        
        # Parse date range
        try:
            start_date, end_date = date_range.split(',')
            start_date = start_date.strip()
            end_date = end_date.strip()
            
            # Validate date formats
            if not validate_date(start_date) or not validate_date(end_date):
                return "Invalid date format. Please use YYYY-MM-DD format for both dates."
            
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date range format. Please use 'start_date,end_date' format (e.g., '2024-01-01,2024-01-31')."
        
        appointments_df = load_appointments()
        
        # Convert datetime column to date for comparison
        appointments_df['date'] = pd.to_datetime(appointments_df['datetime']).dt.date
        mask = (appointments_df['date'] >= start_dt.date()) & (appointments_df['date'] <= end_dt.date())
        range_appointments = appointments_df[mask]
        
        if range_appointments.empty:
            result = f"No appointments found between {start_date} and {end_date}."
        else:
            # Save to CSV
            output_file = f"data/reports/appointments_{start_date}_to_{end_date}.csv"
            ensure_directory_exists(output_file)
            
            save_to_csv(range_appointments, output_file)
            result = f"Appointments export generated: {output_file}"
        
        # Log the tool execution
        log_tool_execution("export_appointments", {"date_range": date_range}, result)
        
        return result
    except Exception as e:
        error_msg = f"Error exporting appointments: {str(e)}"
        logger.error(error_msg)
        return error_msg