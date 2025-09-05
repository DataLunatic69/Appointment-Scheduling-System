from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from utils.logging_config import setup_logging, get_logger, log_agent_operation
from config import LOGGING_CONFIG, AGENT_CONFIG
import os
import time
from datetime import datetime

# Import agents (make sure these are properly defined in your project)
from .patient_agent import patient_agent
from .scheduling_agent import scheduling_agent
from .insurance_agent import insurance_agent
from .communication_agent import communication_agent
from .data_export_agent import data_export_agent

# Load environment variables
load_dotenv()

# Set up logging
setup_logging(**LOGGING_CONFIG)
logger = get_logger(__name__, "supervisor_agent")

# Initialize memory saver for conversation tracking
memory = MemorySaver()
logger.info("Initialized memory saver for conversation tracking")

def create_supervisor_agent():
    """Create and return a configured supervisor agent."""
    logger.info("Creating supervisor agent")
    log_agent_operation(logger, "supervisor_creation", {
        "model": AGENT_CONFIG["model_name"],
        "agent_count": 5,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # Initialize the model
        logger.debug(f"Initializing chat model: {AGENT_CONFIG['model_name']}")
        model = init_chat_model(AGENT_CONFIG["model_name"])
        
        # Define agent list
        agents = [patient_agent, scheduling_agent, insurance_agent, communication_agent, data_export_agent]
        agent_names = [agent.name for agent in agents]
        logger.info(f"Configured agents: {agent_names}")
        
        # Create supervisor prompt
        supervisor_prompt = (
            "You are a supervisor managing a team of specialized agents in a healthcare scheduling system.\n"
            "Your agents are:\n"
            "- patient_agent: Handles patient information management\n"
            "- scheduling_agent: Manages appointment scheduling\n"
            "- insurance_agent: Handles insurance verification\n"
            "- communication_agent: Manages patient communications\n"
            "- data_export_agent: Handles reporting and data export\n"
            "Assign work to the appropriate agent based on the user's request.\n"
            "Assign one agent at a time, do not call agents in parallel.\n"
            "Do not do any work yourself."
        )
        
        logger.debug("Creating supervisor with configuration")
        supervisor_instance = create_supervisor(
            model=model,
            agents=agents,
            prompt=supervisor_prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile(checkpointer=memory)
        
        logger.info("Supervisor agent created successfully")
        return supervisor_instance
        
    except Exception as e:
        logger.error(f"Error creating supervisor agent: {str(e)}", exc_info=True)
        raise

# Create the supervisor instance
logger.info("Initializing supervisor agent instance")
supervisor = create_supervisor_agent()
logger.info("Supervisor agent ready for operation")