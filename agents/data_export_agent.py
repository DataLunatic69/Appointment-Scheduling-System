from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.export_tools import generate_daily_schedule, generate_patient_report, export_appointments
from utils.logging_utils import logger, log_agent_operation
from datetime import datetime

def create_data_export_agent():
    """Create and configure the data export agent."""
    logger.info("Initializing data export agent")
    
    # Create tool instances
    export_tools = [generate_daily_schedule, generate_patient_report, export_appointments]
    
    # Log the tools being used
    log_agent_operation("agent_initialization", {
        "agent_name": "data_export_agent",
        "tools": ["generate_daily_schedule", "generate_patient_report", "export_appointments"],
        "timestamp": datetime.now().isoformat()
    })
    
    # Create the agent
    agent = create_react_agent(
        model=init_chat_model("openai:gpt-4.1"),
        tools=export_tools,
        prompt=(
            "You are a data export agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Use your tools to handle data export tasks\n"
            "- Assist ONLY with data export tasks: generating daily schedules, patient reports, or appointment exports.\n"
            "- After you're done with your tasks, respond to the supervisor directly.\n"
            "- Respond with the results of your work.\n"
            "- If you need more information, ask the supervisor for clarification."
        ),
        name="data_export_agent",
    )
    
    logger.info("Data export agent initialized successfully")
    return agent

# Create the agent instance
data_export_agent = create_data_export_agent()