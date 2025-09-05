import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from agents.supervisor import supervisor
from langchain_core.messages import HumanMessage
import json
import os
import uuid
import re
from utils.logging_utils import logger, log_agent_operation

# Page configuration
st.set_page_config(
    page_title="Healthcare Scheduling System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2ca02c;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-container {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-height: 400px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .assistant-message {
        background-color: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .log-entry {
        font-family: monospace;
        font-size: 0.8rem;
        padding: 0.2rem;
        border-bottom: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "tool_executions" not in st.session_state:
    st.session_state.tool_executions = []

# Sidebar for system information
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏥 Healthcare Scheduling</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Display thread ID for debugging
    st.markdown("**Conversation ID:**")
    st.code(st.session_state.thread_id[:8] + "...")
    
    # Quick actions
    st.markdown("### Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Today's Appointments", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Show today's appointments"})
    
    with col2:
        if st.button("📊 System Status", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What is the system status?"})
    
    # Data management
    st.markdown("---")
    st.markdown("### Data Management")
    
    if st.button("🔄 Generate Sample Data", use_container_width=True):
        # This would call the data generator
        st.info("Sample data generation would run here")
    
    if st.button("📤 Export Reports", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Export all appointment reports"})
    
    # System info
    st.markdown("---")
    st.markdown("### System Information")
    st.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Main content area
st.markdown("<h1 class='main-header'>AI Healthcare Scheduling System</h1>", unsafe_allow_html=True)
st.markdown("Interact with the multi-agent system using natural language.")

# Create tabs for different functionalities
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Chat", "Statistics", "Recent Activity", "Tool Executions", "System Logs"])

with tab1:
    # Display chat messages
    st.markdown("<h3 class='sub-header'>Conversation</h3>", unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'><strong>Assistant:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("How can I help with healthcare scheduling today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process the query with the supervisor agent
        with st.spinner("🤔 Processing your request..."):
            try:
                # Log the user input
                log_agent_operation("user_input", {
                    "prompt": prompt,
                    "thread_id": st.session_state.thread_id,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Create config with thread_id for the checkpointer
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                # Process the query
                response = supervisor.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config=config
                )
                
                # Extract the final response
                final_response = response["messages"][-1].content
                
                # Display the response
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "query": prompt,
                    "response": final_response
                })
                
                # Rerun to update the UI
                st.rerun()
                
            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

with tab2:
    st.markdown("<h3 class='sub-header'>System Statistics</h3>", unsafe_allow_html=True)
    
    try:
        # Load and display patient count
        patients_df = pd.read_csv("data/patients.csv")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Patients", len(patients_df))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Load and display appointment count
        appointments_df = pd.read_excel("data/appointments.xlsx", sheet_name="Appointments")
        today_appointments = appointments_df[
            pd.to_datetime(appointments_df['datetime']).dt.date == datetime.now().date()
        ]
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Today's Appointments", len(today_appointments))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Load insurance data
        insurance_df = pd.read_excel("data/insurance_plans.xlsx", sheet_name="Verification")
        verified_count = len(insurance_df[insurance_df['verification_status'] == 'verified'])
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Verified Insurance", f"{verified_count}/{len(insurance_df)}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display upcoming appointments
        st.markdown("#### Upcoming Appointments")
        upcoming = appointments_df[
            pd.to_datetime(appointments_df['datetime']) >= datetime.now()
        ].sort_values('datetime').head(5)
        
        if not upcoming.empty:
            for _, appt in upcoming.iterrows():
                st.info(f"**{appt['datetime']}**: Patient {appt['patient_id']} with Doctor {appt['doctor_id']}")
        else:
            st.info("No upcoming appointments")
            
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

with tab3:
    st.markdown("<h3 class='sub-header'>Recent Activity</h3>", unsafe_allow_html=True)
    
    if st.session_state.conversation_history:
        for i, item in enumerate(reversed(st.session_state.conversation_history[-10:])):
            st.markdown(f"**{item['timestamp']}**")
            st.markdown(f"**Query:** {item['query']}")
            st.markdown(f"**Response:** {item['response']}")
            
            if i < len(st.session_state.conversation_history[-10:]) - 1:
                st.markdown("---")
    else:
        st.info("No recent activity to display")

with tab4:
    st.markdown("<h3 class='sub-header'>Tool Executions</h3>", unsafe_allow_html=True)
    
    if st.session_state.tool_executions:
        for i, execution in enumerate(reversed(st.session_state.tool_executions[-10:])):
            st.markdown(f"**{execution['timestamp']}**: {execution['tool']}")
            st.markdown(f"*Parameters:* {execution['parameters']}")
            st.markdown(f"*Result:* {execution['result']}")
            
            if i < len(st.session_state.tool_executions[-10:]) - 1:
                st.markdown("---")
    else:
        st.info("No tool executions to display")

with tab5:
    st.markdown("<h3 class='sub-header'>System Logs</h3>", unsafe_allow_html=True)
    
    try:
        # Read and display the latest log file
        log_dir = "logs"
        if os.path.exists(log_dir):
            log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)
            
            if log_files:
                latest_log = os.path.join(log_dir, log_files[0])
                
                with open(latest_log, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                
                # Display the last 50 log entries
                st.markdown(f"**Latest log file:** {log_files[0]}")
                
                log_container = st.container()
                with log_container:
                    for log in logs[-50:]:
                        # Parse log entry for better display
                        if '|' in log:
                            parts = log.split('|')
                            if len(parts) >= 5:
                                timestamp = parts[0].strip()
                                level = parts[1].strip()
                                module = parts[2].strip()
                                function = parts[3].strip()
                                message = '|'.join(parts[4:]).strip()
                                
                                # Color code based on log level
                                if level == 'ERROR':
                                    st.markdown(f"<div class='log-entry' style='color: red;'>{log}</div>", unsafe_allow_html=True)
                                elif level == 'WARNING':
                                    st.markdown(f"<div class='log-entry' style='color: orange;'>{log}</div>", unsafe_allow_html=True)
                                elif level == 'INFO':
                                    st.markdown(f"<div class='log-entry' style='color: blue;'>{log}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)
            else:
                st.info("No log files found")
        else:
            st.info("Log directory does not exist")
    except Exception as e:
        st.error(f"Error reading logs: {str(e)}")

# Add a function to log tool executions
def log_tool_execution(tool_name: str, parameters: dict, result: str):
    """Log tool execution details."""
    st.session_state.tool_executions.append({
        "tool": tool_name,
        "parameters": parameters,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })