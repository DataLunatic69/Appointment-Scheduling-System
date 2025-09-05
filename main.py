from utils.logging_utils import logger, setup_logging
from agents.supervisor import supervisor
from langchain_core.messages import HumanMessage
import uuid

def main():
    """Main entry point for the healthcare scheduling system."""
    # Setup logging
    setup_logging()
    logger.info("Starting healthcare scheduling system")
    
    # Example usage
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Test query
    query = "Show me information for patient P10001"
    
    print(f"Processing query: {query}")
    response = supervisor.invoke(
        {"messages": [HumanMessage(content=query)]},
        config=config
    )
    
    print(f"Response: {response['messages'][-1].content}")
    logger.info("Healthcare scheduling system completed successfully")

if __name__ == "__main__":
    main()