import pandas as pd
from datetime import datetime, timedelta
import os

def generate_daily_schedule(date_str: str) -> str:
    """Generate daily schedule report."""
    try:
        appointments_df = pd.read_excel("data/appointments.xlsx", sheet_name='Appointments')
        appointments_df['date'] = pd.to_datetime(appointments_df['datetime']).dt.date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        daily_appointments = appointments_df[appointments_df['date'] == target_date]
        
        if daily_appointments.empty:
            return f"No appointments found for {date_str}."
        
        # Merge with patient and doctor info
        patients_df = pd.read_csv("data/patients.csv")
        doctors_df = pd.read_excel("data/appointments.xlsx", sheet_name='Doctors')
        
        daily_schedule = daily_appointments.merge(patients_df, on='patient_id', how='left')
        daily_schedule = daily_schedule.merge(doctors_df, on='doctor_id', how='left')
        
        # Save to CSV
        output_file = f"data/reports/daily_schedule_{date_str}.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        daily_schedule.to_csv(output_file, index=False)
        return f"Daily schedule report generated: {output_file}"
    except Exception as e:
        return f"Error generating daily schedule: {str(e)}"

def generate_patient_report(patient_id: str) -> str:
    """Create patient history report."""
    try:
        patients_df = pd.read_csv("data/patients.csv")
        if patient_id not in patients_df['patient_id'].values:
            return f"Patient with ID {patient_id} not found."
        
        appointments_df = pd.read_excel("data/appointments.xlsx", sheet_name='Appointments')
        patient_appointments = appointments_df[appointments_df['patient_id'] == patient_id]
        
        if patient_appointments.empty:
            return f"No appointments found for patient {patient_id}."
        
        # Merge with doctor info
        doctors_df = pd.read_excel("data/appointments.xlsx", sheet_name='Doctors')
        patient_report = patient_appointments.merge(doctors_df, on='doctor_id', how='left')
        
        output_file = f"data/reports/patient_report_{patient_id}.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        patient_report.to_csv(output_file, index=False)
        return f"Patient report generated: {output_file}"
    except Exception as e:
        return f"Error generating patient report: {str(e)}"

def export_appointments(date_range: str) -> str:
    """Export appointments for a period."""
    try:
        start_date, end_date = date_range.split(',')
        start_date = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        end_date = datetime.strptime(end_date.strip(), "%Y-%m-%d")
        
        appointments_df = pd.read_excel("data/appointments.xlsx", sheet_name='Appointments')
        appointments_df['date'] = pd.to_datetime(appointments_df['datetime']).dt.date
        mask = (appointments_df['date'] >= start_date.date()) & (appointments_df['date'] <= end_date.date())
        range_appointments = appointments_df[mask]
        
        if range_appointments.empty:
            return f"No appointments found between {start_date.date()} and {end_date.date()}."
        
        output_file = f"data/reports/appointments_{start_date.date()}_to_{end_date.date()}.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        range_appointments.to_csv(output_file, index=False)
        return f"Appointments export generated: {output_file}"
    except Exception as e:
        return f"Error exporting appointments: {str(e)}"