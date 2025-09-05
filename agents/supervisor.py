from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from .patient_agent import patient_agent
from .scheduling_agent import scheduling_agent
from .insurance_agent import insurance_agent
from .communication_agent import communication_agent
from .data_export_agent import data_export_agent

supervisor = create_supervisor(
    model=init_chat_model("openai:gpt-4.1"),
    agents=[patient_agent, scheduling_agent, insurance_agent, communication_agent, data_export_agent],
    prompt=(
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
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()