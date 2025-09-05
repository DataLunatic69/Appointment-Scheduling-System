from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.scheduling_tools import get_doctor_schedule, check_availability, schedule_appointment, reschedule_appointment, cancel_appointment, get_appointments

scheduling_agent = create_react_agent(
    model=init_chat_model("openai:gpt-4.1"),
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