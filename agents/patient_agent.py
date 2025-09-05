from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.patient_tools import get_patient_info, update_patient_info, create_patient, search_patients
from utils.logging_config import setup_logging, get_logger, log_agent_operation
from config import LOGGING_CONFIG, AGENT_CONFIG
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Set up logging
setup_logging(**LOGGING_CONFIG)
logger = get_logger(__name__, "patient_agent")

logger.info("Initializing patient agent")
log_agent_operation(logger, "agent_initialization", {
    "agent_name": "patient_agent",
    "tools": ["get_patient_info", "update_patient_info", "create_patient", "search_patients"],
    "timestamp": datetime.now().isoformat()
})

try:
    patient_agent = create_react_agent(
        model=init_chat_model(AGENT_CONFIG["model_name"]),
        tools=[get_patient_info, update_patient_info, create_patient, search_patients],
        prompt=(
            "You are a patient management agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with patient-related tasks: retrieving, updating, creating, or searching patient information.\n"
            "- After you're done with your tasks, respond to the supervisor directly.\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."
        ),
        name="patient_agent",
    )
    logger.info("Patient agent initialized successfully")
except Exception as e:
    logger.error(f"Error initializing patient agent: {str(e)}", exc_info=True)
    raise