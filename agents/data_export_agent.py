from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.export_tools import generate_daily_schedule, generate_patient_report, export_appointments

data_export_agent = create_react_agent(
    model=init_chat_model("openai:gpt-4.1"),
    tools=[generate_daily_schedule, generate_patient_report, export_appointments],
    prompt=(
        "You are a data export agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with data export tasks: generating daily schedules, patient reports, or appointment exports.\n"
        "- After you're done with your tasks, respond to the supervisor directly.\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="data_export_agent",
)