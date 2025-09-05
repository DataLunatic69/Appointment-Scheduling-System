from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.communication_tools import send_appointment_reminder, send_followup, send_intake_form

communication_agent = create_react_agent(
    model=init_chat_model("openai:gpt-4.1"),
    tools=[send_appointment_reminder, send_followup, send_intake_form],
    prompt=(
        "You are a communication agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with communication-related tasks: sending reminders, follow-ups, or intake forms.\n"
        "- After you're done with your tasks, respond to the supervisor directly.\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="communication_agent",
)