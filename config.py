"""
Configuration settings for the Healthcare Scheduling System.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_dir": os.getenv("LOG_DIR", "logs"),
    "enable_console": os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true",
    "enable_file": os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true",
    "enable_structured": os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true",
    "max_file_size": int(os.getenv("MAX_LOG_FILE_SIZE", "10485760")),  # 10MB
    "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
}

# Application Configuration
APP_CONFIG = {
    "app_name": "Healthcare Scheduling System",
    "version": "1.0.0",
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "thread_id_length": 8
}

# Data Configuration
DATA_CONFIG = {
    "patients_file": "data/patients.csv",
    "appointments_file": "data/appointments.xlsx",
    "doctor_schedules_file": "data/doctor_schedules.xlsx",
    "insurance_file": "data/insurance_plans.xlsx",
    "email_templates_file": "data/templates/email_templates.json"
}

# Email Configuration
EMAIL_CONFIG = {
    "gmail_user": os.getenv("GMAIL_USER", "your_email@gmail.com"),
    "gmail_app_password": os.getenv("GMAIL_APP_PASSWORD", "your_app_password"),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465
}

# Individual file constants for backward compatibility
DATA_DIR = "data"
TEMPLATES_DIR = "data/templates"
PATIENTS_FILE = DATA_CONFIG["patients_file"]
APPOINTMENTS_FILE = DATA_CONFIG["appointments_file"]
DOCTOR_SCHEDULE_FILE = DATA_CONFIG["doctor_schedules_file"]
INSURANCE_FILE = DATA_CONFIG["insurance_file"]
EMAIL_TEMPLATES_FILE = DATA_CONFIG["email_templates_file"]

# Email constants for backward compatibility
GMAIL_USER = EMAIL_CONFIG["gmail_user"]
GMAIL_APP_PASSWORD = EMAIL_CONFIG["gmail_app_password"]

# Agent Configuration
AGENT_CONFIG = {
    "model_name": "openai:gpt-4.1",
    "max_iterations": int(os.getenv("MAX_AGENT_ITERATIONS", "10")),
    "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.1"))
}
