import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from config import DATA_DIR, PATIENTS_FILE, APPOINTMENTS_FILE, DOCTOR_SCHEDULE_FILE, INSURANCE_FILE, TEMPLATES_DIR, EMAIL_TEMPLATES_FILE

def generate_sample_data():
    """Generate sample data for the healthcare scheduling system."""
    
    # Create directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    
    # Generate patients data
    patients_data = {
        'patient_id': ['P10001', 'P10002', 'P10003', 'P10004', 'P10005', 'P10006', 'P10007', 'P10008'],
        'first_name': ['John', 'Jane', 'Robert', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa'],
        'last_name': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson'],
        'date_of_birth': ['1980-05-15', '1990-08-22', '1975-12-03', '1988-04-18', '1965-11-30', '1995-02-14', '1982-07-09', '1978-09-25'],
        'phone': ['555-1234', '555-5678', '555-9012', '555-3456', '555-7890', '555-2345', '555-6789', '555-0123'],
        'email': [
            'john.doe@email.com', 
            'jane.smith@email.com', 
            'robert.j@email.com', 
            'sarah.w@email.com', 
            'michael.b@email.com',
            'emily.d@email.com',
            'david.m@email.com',
            'lisa.w@email.com'
        ],
        'insurance_provider': ['HealthPlus', 'MedCare', 'HealthPlus', 'WellnessInc', 'MedCare', 'HealthPlus', 'WellnessInc', 'MedCare'],
        'insurance_id': ['INS1001', 'INS1002', 'INS1003', 'INS1004', 'INS1005', 'INS1006', 'INS1007', 'INS1008'],
        'primary_doctor': ['D10001', 'D10002', 'D10001', 'D10003', 'D10002', 'D10003', 'D10001', 'D10002'],
        'created_date': [
            '2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', 
            '2024-05-22', '2024-06-18', '2024-07-03', '2024-08-12'
        ]
    }
    
    patients_df = pd.DataFrame(patients_data)
    patients_df.to_csv(PATIENTS_FILE, index=False)
    print(f"Generated patient data: {PATIENTS_FILE}")
    
    # Generate appointments data
    appointments_data = {
        'appointment_id': ['A10001', 'A10002', 'A10003', 'A10004', 'A10005', 'A10006', 'A10007', 'A10008'],
        'patient_id': ['P10001', 'P10002', 'P10003', 'P10004', 'P10005', 'P10006', 'P10007', 'P10008'],
        'doctor_id': ['D10001', 'D10002', 'D10001', 'D10003', 'D10002', 'D10003', 'D10001', 'D10002'],
        'datetime': [
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 10:00'),
            (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d 14:30'),
            (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d 09:15'),
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 11:00'),
            (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d 15:45'),
            (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d 16:30'),
            (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d 13:00'),
            (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d 10:30')
        ],
        'status': ['scheduled', 'scheduled', 'scheduled', 'scheduled', 'scheduled', 'scheduled', 'scheduled', 'scheduled'],
        'notes': [
            'Routine checkup', 
            'Follow-up visit', 
            'Annual physical', 
            'Consultation', 
            'Vaccination', 
            'Blood test',
            'Dermatology consultation',
            'Cardiology follow-up'
        ]
    }
    
    doctors_data = {
        'doctor_id': ['D10001', 'D10002', 'D10003', 'D10004'],
        'name': ['Dr. Alice Johnson', 'Dr. Bob Brown', 'Dr. Carol Davis', 'Dr. Daniel White'],
        'specialization': ['Cardiology', 'Neurology', 'Pediatrics', 'Dermatology'],
        'contact_info': ['555-9876', '555-5432', '555-1098', '555-6543']
    }
    
    # Create Excel writer object
    with pd.ExcelWriter(APPOINTMENTS_FILE, engine='openpyxl') as writer:
        pd.DataFrame(appointments_data).to_excel(writer, sheet_name='Appointments', index=False)
        pd.DataFrame(doctors_data).to_excel(writer, sheet_name='Doctors', index=False)
    
    print(f"Generated appointments data: {APPOINTMENTS_FILE}")
    
    # Generate doctor schedule data
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
    
    schedule_data = {
        'doctor_id': [],
        'date': [],
        'time_slots': []
    }
    
    for doctor in doctors_data['doctor_id']:
        for date in dates:
            # Generate available time slots (9 AM to 5 PM with 30-minute intervals)
            slots = []
            for hour in range(9, 17):
                for minute in [0, 30]:
                    slots.append(f"{hour:02d}:{minute:02d}")
            
            # Remove some random slots to simulate busy schedule
            remove_count = np.random.randint(2, 5)
            for _ in range(remove_count):
                if slots:
                    slots.pop(np.random.randint(0, len(slots)))
            
            schedule_data['doctor_id'].append(doctor)
            schedule_data['date'].append(date)
            schedule_data['time_slots'].append(','.join(slots))
    
    schedule_df = pd.DataFrame(schedule_data)
    schedule_df.to_excel(DOCTOR_SCHEDULE_FILE, index=False)
    print(f"Generated doctor schedule data: {DOCTOR_SCHEDULE_FILE}")
    
    # Generate insurance data
    plans_data = {
        'insurance_id': ['INS1001', 'INS1002', 'INS1003', 'INS1004', 'INS1005', 'INS1006', 'INS1007', 'INS1008'],
        'provider_name': ['HealthPlus', 'MedCare', 'HealthPlus', 'WellnessInc', 'MedCare', 'HealthPlus', 'WellnessInc', 'MedCare'],
        'plan_name': ['Gold Plan', 'Silver Plan', 'Platinum Plan', 'Basic Plan', 'Premium Plan', 'Gold Plan', 'Basic Plan', 'Silver Plan'],
        'coverage_details': [
            'Covers most procedures with low copay',
            'Basic coverage with moderate copay',
            'Comprehensive coverage with minimal copay',
            'Essential health benefits only',
            'Full coverage including specialist visits',
            'Covers most procedures with low copay',
            'Essential health benefits only',
            'Basic coverage with moderate copay'
        ]
    }
    
    verification_data = {
        'patient_id': ['P10001', 'P10002', 'P10003', 'P10004', 'P10005', 'P10006', 'P10007', 'P10008'],
        'verification_status': ['verified', 'verified', 'pending', 'verified', 'verified', 'verified', 'pending', 'verified'],
        'last_verified': [
            (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
            '',
            (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=25)).strftime('%Y-%m-%d'),
            '',
            (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        ],
        'copay_amount': [20, 30, 0, 25, 15, 20, 0, 30]
    }
    
    # Create Excel writer object
    with pd.ExcelWriter(INSURANCE_FILE, engine='openpyxl') as writer:
        pd.DataFrame(plans_data).to_excel(writer, sheet_name='Plans', index=False)
        pd.DataFrame(verification_data).to_excel(writer, sheet_name='Verification', index=False)
    
    print(f"Generated insurance data: {INSURANCE_FILE}")
    
    # Generate email templates
    email_templates = {
        "reminder": "Dear Patient,\n\nYour appointment with {doctor} is scheduled for {datetime}.\n\nPlease arrive 15 minutes early to complete any necessary paperwork.\n\nIf you need to reschedule or cancel, please contact us at least 24 hours in advance.\n\nBest regards,\nHealthcare Scheduling System",
        "followup": "Dear Patient,\n\nThank you for your recent appointment with {doctor}.\n\nWe would appreciate it if you could take a moment to share your experience by completing our brief survey: https://example.com/survey\n\nYour feedback helps us improve our services.\n\nBest regards,\nHealthcare Scheduling System",
        "intake": "Dear Patient,\n\nBefore your appointment, please complete our intake form at https://example.com/intake.\n\nCompleting this form in advance will help us serve you better and reduce your wait time.\n\nIf you have any questions, please don't hesitate to contact us.\n\nBest regards,\nHealthcare Scheduling System"
    }
    
    with open(EMAIL_TEMPLATES_FILE, 'w') as f:
        json.dump(email_templates, f, indent=2)
    
    print(f"Generated email templates: {EMAIL_TEMPLATES_FILE}")
    print("\n✅ Sample data generation completed successfully!")
    print("\n📋 Generated sample data includes:")
    print(f"   - 8 patients with IDs: P10001 to P10008")
    print(f"   - 4 doctors with IDs: D10001 to D10004")
    print(f"   - 8 appointments with IDs: A10001 to A10008")
    print(f"   - Doctor schedules for the next 7 days")
    print(f"   - Insurance information for all patients")
    print(f"   - Email templates for communications")

if __name__ == "__main__":
    generate_sample_data()