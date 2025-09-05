from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.scheduling_tools import get_doctor_schedule, check_availability, schedule_appointment, reschedule_appointment, cancel_appointment, get_appointments
from utils.logging_config import setup_logging, get_logger, log_agent_operation
from config import LOGGING_CONFIG, AGENT_CONFIG
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Set up logging
setup_logging(**LOGGING_CONFIG)
logger = get_logger(__name__, "scheduling_agent")

logger.info("Initializing scheduling agent")
log_agent_operation(logger, "agent_initialization", {
    "agent_name": "scheduling_agent",
    "tools": ["get_doctor_schedule", "check_availability", "schedule_appointment", "reschedule_appointment", "cancel_appointment", "get_appointments"],
    "timestamp": datetime.now().isoformat()
})

try:
    scheduling_agent = create_react_agent(
        model=init_chat_model(AGENT_CONFIG["model_name"]),
        tools=[get_doctor_schedule, check_availability, schedule_appointment, reschedule_appointment, cancel_appointment, get_appointments],
        prompt=(
            "You are a scheduling agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with scheduling-related tasks: checking availability, scheduling, rescheduling, or canceling appointments.\n"
            "- After you're done with your tasks, respond to the supervisor directly.\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."
        ),
        name="scheduling_agent",
    )
    logger.info("Scheduling agent initialized successfully")
except Exception as e:
    logger.error(f"Error initializing scheduling agent: {str(e)}", exc_info=True)
    raise