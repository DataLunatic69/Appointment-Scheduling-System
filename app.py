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

# Modern Healthcare CSS with improved chat interface
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #1a73e8;
        --primary-dark: #0d47a1;
        --secondary-color: #2e7d32;
        --accent-color: #7b1fa2;
        --success-color: #388e3c;
        --warning-color: #f57c00;
        --error-color: #d32f2f;
        --info-color: #0288d1;
        --text-primary: #212121;
        --text-secondary: #546e7a;
        --text-muted: #78909c;
        --bg-primary: #ffffff;
        --bg-secondary: #f5f7fa;
        --bg-tertiary: #eceff1;
        --border-color: #cfd8dc;
        --border-light: #e2e8f0;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
    }
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: var(--bg-secondary);
        line-height: 1.6;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    /* Chat container - Modern redesign */
    .chat-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 0;
        border-radius: var(--radius-xl);
        margin-bottom: 1.5rem;
        height: 70vh;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        display: flex;
        flex-direction: column;
        position: relative;
    }
    
    /* Chat header */
    .chat-header {
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .chat-header h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chat-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Chat messages area */
    .chat-messages {
        flex: 1;
        padding: 1.5rem;
        overflow-y: auto;
        background: #ffffff;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    /* Chat input area */
    .chat-input-area {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-top: 1px solid #e2e8f0;
        border-radius: 0 0 var(--radius-xl) var(--radius-xl);
    }
    
    /* Message styling - Improved with better layout */
    .message-container {
        display: flex;
        margin-bottom: 1.25rem;
        width: 100%;
        animation: fadeInUp 0.3s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message-container {
        justify-content: flex-end;
    }
    
    .assistant-message-container {
        justify-content: flex-start;
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        padding: 1.25rem;
        border-radius: 1.25rem;
        border-bottom-right-radius: 0.5rem;
        max-width: 75%;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        color: white;
        line-height: 1.6;
        margin-left: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        padding: 1.25rem;
        border-radius: 1.25rem;
        border-bottom-left-radius: 0.5rem;
        max-width: 75%;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        color: var(--text-primary);
        line-height: 1.7;
        margin-right: 2rem;
    }
    
    .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .assistant-message .message-header {
        color: var(--text-secondary);
    }
    
    /* Welcome message styling */
    .welcome-message {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
        font-style: italic;
        margin: auto;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        margin-bottom: 1.5rem;
        padding: 1.25rem;
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .sidebar-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online { background-color: var(--success-color); }
    .status-offline { background-color: var(--error-color); }
    .status-pending { background-color: var(--warning-color); }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: var(--primary-dark);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Input styling - Enhanced for chat */
    .stTextInput > div > div > input {
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
    }
    
    /* Chat input specific styling */
    .chat-input-area .stTextInput > div > div > input {
        border-radius: 1.5rem;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.25rem;
        font-size: 1rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .chat-input-area .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        transform: translateY(-1px);
    }
    
    .chat-input-area .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
        font-style: italic;
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: var(--radius-sm);
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: var(--radius-sm);
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Improved text contrast */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        color: white;
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Sidebar styling - Dark theme with better visibility */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 2px solid #334155;
    }
    
    .sidebar-section {
        margin-bottom: 1.5rem;
        padding: 1.25rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-lg);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .sidebar-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff !important;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar text styling - ALL WHITE for better visibility */
    .sidebar-section p, .sidebar-section div, .sidebar-section span, .sidebar-section label {
        color: #ffffff !important;
    }
    
    .sidebar-section strong {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .sidebar-section small {
        color: #e2e8f0 !important;
    }
    
    .sidebar-section code {
        color: #10b981 !important;
        background: rgba(0, 0, 0, 0.3) !important;
        padding: 0.25rem 0.5rem !important;
        border-radius: 0.25rem !important;
        font-family: 'Fira Code', monospace !important;
    }
    
    /* Force all sidebar text to be white */
    .css-1d391kg * {
        color: #ffffff !important;
    }
    
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span, .css-1d391kg label, .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 {
        color: #ffffff !important;
    }
    
    /* Sidebar buttons */
    .sidebar-section .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-section .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar input fields */
    .sidebar-section .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-md);
        padding: 0.75rem;
        color: #f1f5f9;
        font-size: 0.9rem;
    }
    
    .sidebar-section .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .sidebar-section .stTextInput > div > div > input::placeholder {
        color: #94a3b8;
    }
    
    /* Sidebar code blocks */
    .sidebar-section .stCode {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-sm);
        padding: 0.5rem;
        color: #10b981;
        font-family: 'Fira Code', monospace;
        font-size: 0.8rem;
    }
    
    /* Sidebar alerts - improved visibility */
    .sidebar-section .stAlert {
        background: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: var(--radius-md) !important;
        color: #10b981 !important;
        font-weight: 500 !important;
    }
    
    .sidebar-section .stAlert[data-testid="alert-warning"] {
        background: rgba(245, 158, 11, 0.15) !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        color: #f59e0b !important;
    }
    
    .sidebar-section .stAlert[data-testid="alert-error"] {
        background: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #ef4444 !important;
    }
    
    /* Ensure all text in sidebar is visible */
    .sidebar-section * {
        color: inherit !important;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online { background-color: #10b981; }
    .status-offline { background-color: #ef4444; }
    .status-pending { background-color: #f59e0b; }
    
    /* Message styling improvements */
    .message-container {
        margin-bottom: 1rem;
    }
    
    .user-message-container {
        display: flex;
        justify-content: flex-end;
    }
    
    .assistant-message-container {
        display: flex;
        justify-content: flex-start;
    }
    
    .message-header {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        color: var(--text-secondary);
    }
    
    .message-content {
        line-height: 1.6;
        font-size: 1rem;
    }
    
    .welcome-message {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
        background: var(--bg-tertiary);
        border-radius: var(--radius-lg);
        border: 2px dashed var(--border-color);
    }
    
    .welcome-message h3 {
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    /* Remove any unwanted white elements */
    .stTextInput > div > div > input:not(:focus) {
        background-color: var(--bg-primary) !important;
    }
    
    /* Improve chat input visibility */
    .stChatInput > div > div > div > div > div > input {
        background-color: var(--bg-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }
    
    .stChatInput > div > div > div > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
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

if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False

# Sidebar for system information
with st.sidebar:
    # Header
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #f1f5f9; margin-bottom: 0; font-size: 1.5rem;'>🏥 Healthcare AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #cbd5e1; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Multi-Agent System</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # OpenAI API Key Configuration
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>🔑 API Key</div>", unsafe_allow_html=True)
    
    # Check if OpenAI key is already set
    current_key = os.getenv('OPENAI_API_KEY', '')
    if current_key and st.session_state.api_key_configured:
        st.success("✅ API Key Configured")
        if st.button("🔄 Update Key", use_container_width=True, key="update_key"):
            st.session_state.show_key_input = True
            st.session_state.api_key_configured = False
    else:
        st.warning("⚠️ API Key Required")
        st.session_state.show_key_input = True
    
    # Show key input if needed
    if st.session_state.get('show_key_input', True):
        new_key = st.text_input(
            "OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Required for AI agents to function",
            key="api_key_input"
        )
        
        if st.button("💾 Save Key", use_container_width=True, key="save_key"):
            if new_key and new_key.startswith('sk-'):
                os.environ['OPENAI_API_KEY'] = new_key
                st.session_state.show_key_input = False
                st.session_state.api_key_configured = True
                st.success("✅ Key Saved!")
                st.rerun()
            else:
                st.error("❌ Invalid API key format")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>⚡ Quick Actions</div>", unsafe_allow_html=True)
    
    if st.button("📅 Today's Appointments", use_container_width=True, key="today_appt"):
        st.session_state.messages.append({"role": "user", "content": "Show today's appointments"})
        st.rerun()
    
    if st.button("👥 Manage Patients", use_container_width=True, key="patient_mgmt"):
        st.session_state.messages.append({"role": "user", "content": "Help me manage patient information"})
        st.rerun()
    
    if st.button("🔍 Check Availability", use_container_width=True, key="check_avail"):
        st.session_state.messages.append({"role": "user", "content": "Check doctor availability for appointments"})
        st.rerun()
    
    if st.button("📊 View Statistics", use_container_width=True, key="view_stats"):
        st.session_state.messages.append({"role": "user", "content": "Show me the system statistics"})
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System Status
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>📊 System Status</div>", unsafe_allow_html=True)
    
    # Status indicators
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Status:**")
        st.markdown("<span class='status-indicator status-online'></span>Online", unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Agents:**")
        st.markdown("6 Active", unsafe_allow_html=True)
    
    # Session ID with better styling and explanation
    st.markdown("**Session ID:**")
    st.markdown(f"""
    <div style='background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 0.375rem; border: 1px solid rgba(255,255,255,0.1); margin: 0.5rem 0;'>
        <code style='color: #10b981; font-family: monospace; font-size: 0.8rem;'>{st.session_state.thread_id[:8]}...</code>
    </div>
    <small style='color: #94a3b8; font-size: 0.75rem;'>Unique session identifier for debugging</small>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main content area
st.markdown("<h1 class='main-header'>AI Healthcare Scheduling System</h1>", unsafe_allow_html=True)

# Removed welcome banner to eliminate white rectangle

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Statistics", "🔧 Tools"])

with tab1:
    # Modern chat interface
    st.markdown("""
    <div class='chat-container'>
        <div class='chat-header'>
            <h3>💬 Healthcare Assistant</h3>
            <div class='chat-status'>
                <div class='status-dot'></div>
                <span>Online</span>
            </div>
        </div>
        <div class='chat-messages'>
    """, unsafe_allow_html=True)
    
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class='message-container user-message-container'>
                    <div class='user-message'>
                        <div class='message-header'>👤 You</div>
                        <div class='message-content'>{message['content']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='message-container assistant-message-container'>
                    <div class='assistant-message'>
                        <div class='message-header'>🤖 Healthcare Assistant</div>
                        <div class='message-content'>{message['content']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Modern welcome message
        st.markdown("""
        <div style='text-align: center; padding: 3rem 2rem; color: var(--text-secondary);'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🏥</div>
            <h3 style='color: var(--primary-color); margin-bottom: 1rem; font-size: 1.5rem;'>Welcome to Healthcare Assistant</h3>
            <p style='font-size: 1.1rem; margin-bottom: 2rem; opacity: 0.8;'>Your intelligent healthcare scheduling companion</p>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; max-width: 400px; margin: 0 auto;'>
                <div style='background: #f8fafc; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0;'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>📅</div>
                    <div style='font-weight: 600; color: var(--text-primary);'>Appointments</div>
                </div>
                <div style='background: #f8fafc; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0;'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>👥</div>
                    <div style='font-weight: 600; color: var(--text-primary);'>Patients</div>
                </div>
                <div style='background: #f8fafc; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0;'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>👨‍⚕️</div>
                    <div style='font-weight: 600; color: var(--text-primary);'>Doctors</div>
                </div>
                <div style='background: #f8fafc; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0;'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>📊</div>
                    <div style='font-weight: 600; color: var(--text-primary);'>Analytics</div>
                </div>
            </div>
            <p style='margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;'>Start a conversation or use the quick actions in the sidebar</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        <div class='chat-input-area'>
    """, unsafe_allow_html=True)
    
    # Chat input at the bottom
    if prompt := st.chat_input("How can I help with healthcare scheduling today?"):
        # Check if API key is configured
        if not st.session_state.api_key_configured:
            st.error("Please configure your OpenAI API key in the sidebar first.")
            st.stop()
            
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
    
    # Close chat container
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("<h3 class='sub-header'>📊 System Statistics</h3>", unsafe_allow_html=True)
    
    try:
        # Create sample data for demonstration
        sample_patients = [
            {'id': 1, 'name': 'John Doe', 'age': 45, 'last_visit': '2023-10-15'},
            {'id': 2, 'name': 'Jane Smith', 'age': 32, 'last_visit': '2023-10-18'},
            {'id': 3, 'name': 'Robert Johnson', 'age': 61, 'last_visit': '2023-10-20'},
            {'id': 4, 'name': 'Emily Davis', 'age': 28, 'last_visit': '2023-10-22'},
        ]
        
        sample_appointments = [
            {'id': 1, 'patient_id': 1, 'datetime': '2023-10-25 09:00', 'doctor': 'Dr. Smith', 'status': 'scheduled'},
            {'id': 2, 'patient_id': 2, 'datetime': '2023-10-25 10:30', 'doctor': 'Dr. Johnson', 'status': 'confirmed'},
            {'id': 3, 'patient_id': 3, 'datetime': '2023-10-26 11:00', 'doctor': 'Dr. Williams', 'status': 'scheduled'},
            {'id': 4, 'patient_id': 4, 'datetime': '2023-10-26 14:00', 'doctor': 'Dr. Brown', 'status': 'pending'},
        ]
        
        patients_df = pd.DataFrame(sample_patients)
        appointments_df = pd.DataFrame(sample_appointments)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("👥 Total Patients", len(patients_df), delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
        
        today = datetime.now().date()
        today_appointments = appointments_df[appointments_df['datetime'].str.startswith(str(today))]
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("📅 Today's Appointments", len(today_appointments), delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("📋 Total Appointments", len(appointments_df), delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("✅ Confirmed", len(appointments_df[appointments_df['status'] == 'confirmed']), delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display upcoming appointments
        st.markdown("#### 📅 Upcoming Appointments")
        
        if not appointments_df.empty:
            for _, appt in appointments_df.iterrows():
                status = appt.get('status', 'scheduled')
                status_color = "var(--success-color)" if status == "confirmed" else "var(--warning-color)" if status == "pending" else "var(--info-color)"
                st.markdown(f"""
                <div style='background: var(--bg-primary); padding: 1rem; border-radius: var(--radius-md); margin-bottom: 0.5rem; border-left: 4px solid {status_color}'>
                    <strong>📅 {appt['datetime']}</strong><br>
                    Patient {appt['patient_id']} with {appt['doctor']}<br>
                    <small style='color: {status_color};'>Status: {status}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No appointments found")
        
        # System health metrics
        st.markdown("#### 🏥 System Health")
        health_col1, health_col2, health_col3 = st.columns(3)
        
        with health_col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("🤖 Active Agents", "4", delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with health_col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("💬 Messages Today", len(st.session_state.messages), delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with health_col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("🔄 System Uptime", "100%", delta=None)
            st.markdown("</div>", unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

with tab3:
    st.markdown("<h3 class='sub-header'>🔧 Tools & Settings</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'>🛠️ System Tools</div>", unsafe_allow_html=True)
        
        if st.button("🔄 Generate Sample Data", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Generate sample data for the system"})
            st.rerun()
        
        if st.button("📋 Export Reports", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Export all appointment reports"})
            st.rerun()
        
        if st.button("📖 Documentation", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Show me the system documentation and help"})
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'>⚙️ Settings</div>", unsafe_allow_html=True)
        
        # Theme selection
        theme = st.selectbox("Color Theme", ["Light", "Dark", "Auto"])
        
        # Notification preferences
        notifs = st.checkbox("Enable notifications", value=True)
        email_notifs = st.checkbox("Email notifications", value=False)
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("Settings saved successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>🕒 Recent Activity</div>", unsafe_allow_html=True)
    
    if st.session_state.conversation_history:
        for i, item in enumerate(reversed(st.session_state.conversation_history[-5:])):
            st.markdown(f"""
            <div style='margin-bottom: 1rem; padding: 0.75rem; background: var(--bg-tertiary); border-radius: var(--radius-md);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                    <strong>🕒 {datetime.fromisoformat(item['timestamp']).strftime('%H:%M')}</strong>
                    <span style='color: var(--text-secondary); font-size: 0.875rem;'>#{len(st.session_state.conversation_history) - i}</span>
                </div>
                <div style='margin-bottom: 0.5rem; font-size: 0.9rem;'>
                    <strong>💬 Query:</strong> {item['query']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; color: var(--text-muted); padding: 1rem; font-style: italic;'>No recent activity to display.</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Add a function to log tool executions
def log_tool_execution(tool_name: str, parameters: dict, result: str):
    """Log tool execution details."""
    st.session_state.tool_executions.append({
        "tool": tool_name,
        "parameters": parameters,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })