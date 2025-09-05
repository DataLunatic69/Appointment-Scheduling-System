from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.communication_tools import send_appointment_reminder, send_followup, send_intake_form
from utils.logging_utils import logger, log_agent_operation
from datetime import datetime

def create_communication_agent():
    """Create and configure the communication agent."""
    logger.info("Initializing communication agent")
    
    # Create tool instances
    communication_tools = [send_appointment_reminder, send_followup, send_intake_form]
    
    # Log the tools being used
    log_agent_operation("agent_initialization", {
        "agent_name": "communication_agent",
        "tools": ["send_appointment_reminder", "send_followup", "send_intake_form"],
        "timestamp": datetime.now().isoformat()
    })
    
    # Create the agent
    agent = create_react_agent(
        model=init_chat_model("openai:gpt-4.1"),
        tools=communication_tools,
        prompt=(
            "You are a communication agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Use your tools to handle communication-related tasks\n"
            "- Assist ONLY with communication-related tasks: sending reminders, follow-ups, or intake forms.\n"
            "- After you're done with your tasks, respond to the supervisor directly.\n"
            "- Respond with the results of your work.\n"
            "- If you need more information, ask the supervisor for clarification."
        ),
        name="communication_agent",
    )
    
    logger.info("Communication agent initialized successfully")
    return agent

# Create the agent instance
communication_agent = create_communication_agent()