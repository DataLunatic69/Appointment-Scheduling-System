from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from tools.insurance_tools import verify_insurance, check_coverage, get_copay_info

insurance_agent = create_react_agent(
    model=init_chat_model("openai:gpt-4.1"),
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