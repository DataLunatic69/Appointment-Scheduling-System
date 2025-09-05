from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.insurance_tools import verify_insurance, check_coverage, get_copay_info
from utils.logging_config import setup_logging, get_logger, log_agent_operation
from config import LOGGING_CONFIG, AGENT_CONFIG
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Set up logging
setup_logging(**LOGGING_CONFIG)
logger = get_logger(__name__, "insurance_agent")

logger.info("Initializing insurance agent")
log_agent_operation(logger, "agent_initialization", {
    "agent_name": "insurance_agent",
    "tools": ["verify_insurance", "check_coverage", "get_copay_info"],
    "timestamp": datetime.now().isoformat()
})

try:
    insurance_agent = create_react_agent(
        model=init_chat_model(AGENT_CONFIG["model_name"]),
        tools=[verify_insurance, check_coverage, get_copay_info],
        prompt=(
            "You are an insurance agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with insurance-related tasks: verification, coverage checks, copay information.\n"
            "- After you're done with your tasks, respond to the supervisor directly.\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."
        ),
        name="insurance_agent",
    )
    logger.info("Insurance agent initialized successfully")
except Exception as e:
    logger.error(f"Error initializing insurance agent: {str(e)}", exc_info=True)
    raise