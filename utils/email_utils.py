import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from config import GMAIL_USER, GMAIL_APP_PASSWORD
from .validators import validate_email

def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> dict:
    """Send an email using Gmail SMTP server."""
    try:
        # Validate email format
        if not validate_email(to_email):
            return {"success": False, "message": f"Invalid email address: {to_email}"}
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Create server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        
        return {"success": True, "message": f"Email sent successfully to {to_email}"}
    except Exception as e:
        return {"success": False, "message": f"Error sending email: {str(e)}"}

def send_bulk_emails(emails: list, subject: str, body: str, is_html: bool = False) -> dict:
    """Send emails to multiple recipients."""
    results = {
        "total": len(emails),
        "successful": 0,
        "failed": 0,
        "details": []
    }
    
    for email in emails:
        result = send_email(email, subject, body, is_html)
        if result["success"]:
            results["successful"] += 1
        else:
            results["failed"] += 1
        results["details"].append({"email": email, "result": result})
    
    return results

def create_email_template(template_name: str, variables: dict) -> str:
    """Create an email from a template with variables."""
    # This would typically load from a file or database
    templates = {
        "appointment_reminder": """
Dear {patient_name},

Your appointment with {doctor_name} is scheduled for {appointment_time}.

Please arrive 15 minutes early to complete any necessary paperwork.

If you need to reschedule or cancel, please contact us at least 24 hours in advance.

Best regards,
Healthcare Scheduling System
""",
        "follow_up": """
Dear {patient_name},

Thank you for your recent appointment with {doctor_name}.

We would appreciate it if you could take a moment to share your experience by completing our brief survey: {survey_link}

Your feedback helps us improve our services.

Best regards,
Healthcare Scheduling System
""",
        "intake_form": """
Dear {patient_name},

Before your appointment, please complete our intake form at {intake_form_link}.

Completing this form in advance will help us serve you better and reduce your wait time.

If you have any questions, please don't hesitate to contact us.

Best regards,
Healthcare Scheduling System
"""
    }
    
    template = templates.get(template_name, "")
    for key, value in variables.items():
        template = template.replace(f"{{{key}}}", str(value))
    
    return template