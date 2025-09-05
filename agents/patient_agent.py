from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.patient_tools import get_patient_info, update_patient_info, create_patient, search_patients

patient_agent = create_react_agent(
    model=init_chat_model("openai:gpt-4.1"),
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