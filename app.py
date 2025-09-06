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

# Enhanced Modern Healthcare CSS with improved chat interface
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #3b82f6;
        --primary-dark: #1d4ed8;
        --secondary-color: #10b981;
        --accent-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --info-color: #06b6d4;
        --text-primary: #111827;
        --text-secondary: #374151;
        --text-muted: #6b7280;
        --text-white: #ffffff;
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --bg-tertiary: #f3f4f6;
        --bg-dark: #1f2937;
        --bg-darker: #111827;
        --border-color: #e5e7eb;
        --border-light: #f3f4f6;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
    }
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        line-height: 1.6;
    }
    
    /* Hide default Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Welcome container - Initially centered */
    .welcome-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 60vh;
        margin: 2rem 0;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: var(--radius-2xl);
        padding: 3rem;
        box-shadow: var(--shadow-xl);
        border: 1px solid var(--border-color);
        text-align: center;
        max-width: 600px;
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color), var(--secondary-color));
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .welcome-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-color);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .feature-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.875rem;
    }
    
    /* Chat container - Improved positioning */
    .chat-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: var(--radius-2xl);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-xl);
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .chat-container.has-messages {
        height: 70vh;
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 4rem);
        max-width: 1200px;
        z-index: 1000;
    }
    
    .chat-container.welcome-mode {
        position: relative;
        height: auto;
        min-height: 500px;
    }
    
    /* Chat header */
    .chat-header {
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .chat-title {
        margin: 0;
        font-size: 1.125rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .chat-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        opacity: 0.9;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: var(--secondary-color);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* Chat messages area */
    .chat-messages {
        flex: 1;
        padding: 1.5rem;
        overflow-y: auto;
        background: var(--bg-primary);
        display: flex;
        flex-direction: column;
        gap: 1rem;
        min-height: 300px;
    }
    
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: var(--radius-sm);
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: var(--radius-sm);
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Message styling */
    .message-container {
        display: flex;
        margin-bottom: 1rem;
        width: 100%;
        animation: slideInUp 0.3s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
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
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        padding: 1rem 1.25rem;
        border-radius: var(--radius-xl);
        border-bottom-right-radius: var(--radius-sm);
        max-width: 70%;
        box-shadow: var(--shadow-md);
        margin-left: 2rem;
        position: relative;
    }
    
    .user-message::before {
        content: '';
        position: absolute;
        bottom: 0;
        right: -8px;
        width: 0;
        height: 0;
        border-left: 8px solid var(--primary-dark);
        border-bottom: 8px solid transparent;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        color: var(--text-primary);
        padding: 1rem 1.25rem;
        border-radius: var(--radius-xl);
        border-bottom-left-radius: var(--radius-sm);
        max-width: 70%;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        margin-right: 2rem;
        position: relative;
    }
    
    .assistant-message::before {
        content: '';
        position: absolute;
        bottom: 0;
        left: -8px;
        width: 0;
        height: 0;
        border-right: 8px solid #ffffff;
        border-bottom: 8px solid transparent;
    }
    
    .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.8;
    }
    
    .message-content {
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Chat input area */
    .chat-input-area {
        background: var(--bg-secondary);
        padding: 1.25rem 1.5rem;
        border-top: 1px solid var(--border-color);
        border-radius: 0 0 var(--radius-2xl) var(--radius-2xl);
    }
    
    /* Enhanced input styling */
    .stChatInput > div > div > div > div > div > input {
        background: var(--bg-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-xl) !important;
        padding: 1rem 1.25rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stChatInput > div > div > div > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    .stChatInput > div > div > div > div > div > input::placeholder {
        color: var(--text-muted) !important;
        font-style: italic !important;
    }
    
    /* Tab styling improvements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-md);
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-color) !important;
        color: white !important;
        box-shadow: var(--shadow-sm);
    }
    
    /* Statistics and Tools sections - Fixed font colors */
    .metric-card {
        background: var(--bg-primary);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .metric-card h3, .metric-card p, .metric-card div, .metric-card span {
        color: var(--text-primary) !important;
    }
    
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color) !important;
    }
    
    .metric-card .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    /* Content cards for stats and tools */
    .content-card {
        background: var(--bg-primary);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        margin-bottom: 1rem;
    }
    
    .content-card h4, .content-card h5, .content-card h6,
    .content-card p, .content-card div, .content-card span,
    .content-card strong, .content-card em {
        color: var(--text-primary) !important;
    }
    
    .content-card .text-secondary {
        color: var(--text-secondary) !important;
    }
    
    .content-card .text-muted {
        color: var(--text-muted) !important;
    }
    
    /* Appointment cards */
    .appointment-card {
        background: var(--bg-primary);
        padding: 1rem 1.25rem;
        border-radius: var(--radius-md);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 0.75rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .appointment-card:hover {
        transform: translateX(4px);
        box-shadow: var(--shadow-md);
    }
    
    .appointment-card h6, .appointment-card p, .appointment-card div,
    .appointment-card span, .appointment-card strong {
        color: var(--text-primary) !important;
    }
    
    .appointment-card .appointment-time {
        font-weight: 600;
        color: var(--primary-color) !important;
        font-size: 1rem;
    }
    
    .appointment-card .appointment-details {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
    }
    
    .appointment-card .appointment-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .status-confirmed {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color) !important;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-pending {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning-color) !important;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .status-scheduled {
        background: rgba(59, 130, 246, 0.1);
        color: var(--info-color) !important;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* Sidebar styling - Dark theme with better visibility */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        border-right: 2px solid #374151;
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
        color: var(--text-white) !important;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-color);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Force all sidebar text to be white */
    .css-1d391kg *, .sidebar-section * {
        color: var(--text-white) !important;
    }
    
    /* Sidebar buttons */
    .sidebar-section .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white !important;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-section .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-dark), #1e40af);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Sidebar input fields */
    .sidebar-section .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem !important;
        color: var(--text-white) !important;
        font-size: 0.9rem !important;
    }
    
    .sidebar-section .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    .sidebar-section .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
    }
    
    /* Button styling for main content */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--primary-dark);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Tool section styling */
    .tool-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .tool-card {
        background: var(--bg-primary);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        text-align: center;
    }
    
    .tool-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-color);
    }
    
    .tool-card h5, .tool-card p, .tool-card div {
        color: var(--text-primary) !important;
    }
    
    .tool-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .tool-title {
        font-weight: 600;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem;
    }
    
    .tool-description {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    
    /* Activity log styling */
    .activity-item {
        background: var(--bg-primary);
        padding: 1rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .activity-item:hover {
        transform: translateX(4px);
        box-shadow: var(--shadow-sm);
    }
    
    .activity-item h6, .activity-item p, .activity-item div,
    .activity-item span, .activity-item strong {
        color: var(--text-primary) !important;
    }
    
    .activity-time {
        font-weight: 600;
        color: var(--primary-color) !important;
        font-size: 0.875rem;
    }
    
    .activity-query {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }
        
        .tool-grid {
            grid-template-columns: 1fr;
        }
        
        .chat-container.has-messages {
            width: calc(100% - 2rem);
            left: 1rem;
            transform: none;
        }
        
        .user-message, .assistant-message {
            max-width: 85%;
        }
    }
    
    /* Loading states */
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots::after {
        content: '';
        animation: dots 1.5s infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    
    /* Custom alerts */
    .custom-alert {
        padding: 1rem 1.25rem;
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        border: 1px solid;
        font-weight: 500;
    }
    
    .alert-success {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.2);
        color: var(--success-color) !important;
    }
    
    .alert-warning {
        background: rgba(245, 158, 11, 0.1);
        border-color: rgba(245, 158, 11, 0.2);
        color: var(--warning-color) !important;
    }
    
    .alert-error {
        background: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.2);
        color: var(--error-color) !important;
    }
    
    .alert-info {
        background: rgba(6, 182, 212, 0.1);
        border-color: rgba(6, 182, 212, 0.2);
        color: var(--info-color) !important;
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
    st.markdown("<h2 style='text-align: center; color: #ffffff; margin-bottom: 0; font-size: 1.5rem;'>🏥 Healthcare AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #e2e8f0; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Multi-Agent System</p>", unsafe_allow_html=True)
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

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Statistics", "🔧 Tools"])

with tab1:
    # Check if there are messages to determine chat container style
    has_messages = len(st.session_state.messages) > 0
    container_class = "chat-container has-messages" if has_messages else "chat-container welcome-mode"
    
    if not has_messages:
        # Show welcome screen using pure Streamlit components
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Create centered container using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Simple welcome header
            st.markdown("<div style='text-align: center; font-size: 64px; margin: 24px 0;'>🏥</div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; color: #3b82f6; margin-bottom: 16px;'>Healthcare Assistant</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6b7280; font-size: 18px; margin-bottom: 32px;'>Your intelligent healthcare scheduling companion</p>", unsafe_allow_html=True)
            
            # Feature cards using Streamlit columns
            st.markdown("### Quick Access")
            
            feat_col1, feat_col2 = st.columns(2)
            
            with feat_col1:
                st.markdown("<div style='text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px; margin-bottom: 16px; border: 1px solid #e5e7eb;'><div style='font-size: 32px; margin-bottom: 8px;'>📅</div><strong>Appointments</strong></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px; margin-bottom: 16px; border: 1px solid #e5e7eb;'><div style='font-size: 32px; margin-bottom: 8px;'>👨‍⚕️</div><strong>Doctors</strong></div>", unsafe_allow_html=True)
            
            with feat_col2:
                st.markdown("<div style='text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px; margin-bottom: 16px; border: 1px solid #e5e7eb;'><div style='font-size: 32px; margin-bottom: 8px;'>👥</div><strong>Patients</strong></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px; margin-bottom: 16px; border: 1px solid #e5e7eb;'><div style='font-size: 32px; margin-bottom: 8px;'>📊</div><strong>Analytics</strong></div>", unsafe_allow_html=True)
            
            st.markdown("<p style='text-align: center; margin-top: 32px; color: #6b7280; font-style: italic;'>Start a conversation or use the quick actions in the sidebar</p>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Chat container
    st.markdown(f"""
    <div class='{container_class}'>
        <div class='chat-header'>
            <h3 class='chat-title'>💬 Healthcare Assistant</h3>
            <div class='chat-status'>
                <div class='status-dot'></div>
                <span>Online</span>
            </div>
        </div>
        <div class='chat-messages'>
    """, unsafe_allow_html=True)
    
    # Display messages if they exist
    if has_messages:
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
        # Welcome message in chat area
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: var(--text-muted);'>
            <p style='font-size: 1.1rem; font-style: italic;'>
                Welcome! How can I help you with healthcare scheduling today?
            </p>
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
    st.markdown("<h3 class='section-header'>📊 System Statistics</h3>", unsafe_allow_html=True)
    
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
        
        # Metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>👥 Total Patients</div>
                <div class='metric-value'>{len(patients_df)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        today = datetime.now().date()
        today_appointments = appointments_df[appointments_df['datetime'].str.startswith(str(today))]
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>📅 Today's Appointments</div>
                <div class='metric-value'>{len(today_appointments)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>📋 Total Appointments</div>
                <div class='metric-value'>{len(appointments_df)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>✅ Confirmed</div>
                <div class='metric-value'>{len(appointments_df[appointments_df['status'] == 'confirmed'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Upcoming appointments
        st.markdown("<h4 class='section-header'>📅 Upcoming Appointments</h4>", unsafe_allow_html=True)
        
        if not appointments_df.empty:
            for _, appt in appointments_df.iterrows():
                status = appt.get('status', 'scheduled')
                status_class = f"status-{status}"
                
                st.markdown(f"""
                <div class='appointment-card'>
                    <div class='appointment-time'>📅 {appt['datetime']}</div>
                    <div class='appointment-details'>Patient {appt['patient_id']} with {appt['doctor']}</div>
                    <span class='appointment-status {status_class}'>{status}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='custom-alert alert-info'>No appointments found</div>", unsafe_allow_html=True)
        
        # System health metrics
        st.markdown("<h4 class='section-header'>🏥 System Health</h4>", unsafe_allow_html=True)
        
        health_col1, health_col2, health_col3 = st.columns(3)
        
        with health_col1:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>🤖 Active Agents</div>
                <div class='metric-value'>6</div>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>💬 Messages Today</div>
                <div class='metric-value'>{len(st.session_state.messages)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with health_col3:
            st.markdown("""
            <div class='metric-card'>
                <div class='metric-label'>🔄 System Uptime</div>
                <div class='metric-value'>100%</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.markdown(f"<div class='custom-alert alert-error'>Error loading statistics: {str(e)}</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<h3 class='section-header'>🔧 Tools & Settings</h3>", unsafe_allow_html=True)
    
    # Tools grid
    st.markdown("""
    <div class='tool-grid'>
        <div class='tool-card'>
            <span class='tool-icon'>🔄</span>
            <h5 class='tool-title'>Generate Sample Data</h5>
            <p class='tool-description'>Create sample patient and appointment data for testing</p>
        </div>
        <div class='tool-card'>
            <span class='tool-icon'>📋</span>
            <h5 class='tool-title'>Export Reports</h5>
            <p class='tool-description'>Export all appointment reports and analytics</p>
        </div>
        <div class='tool-card'>
            <span class='tool-icon'>📖</span>
            <h5 class='tool-title'>Documentation</h5>
            <p class='tool-description'>View system documentation and help guides</p>
        </div>
        <div class='tool-card'>
            <span class='tool-icon'>⚙️</span>
            <h5 class='tool-title'>System Settings</h5>
            <p class='tool-description'>Configure system preferences and options</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("<h5>🛠️ System Tools</h5>", unsafe_allow_html=True)
        
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
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("<h5>⚙️ Settings</h5>", unsafe_allow_html=True)
        
        # Theme selection
        theme = st.selectbox("Color Theme", ["Light", "Dark", "Auto"])
        
        # Notification preferences
        notifs = st.checkbox("Enable notifications", value=True)
        email_notifs = st.checkbox("Email notifications", value=False)
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.markdown("<div class='custom-alert alert-success'>Settings saved successfully!</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<h5>🕒 Recent Activity</h5>", unsafe_allow_html=True)
    
    if st.session_state.conversation_history:
        for i, item in enumerate(reversed(st.session_state.conversation_history[-5:])):
            st.markdown(f"""
            <div class='activity-item'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                    <span class='activity-time'>🕒 {datetime.fromisoformat(item['timestamp']).strftime('%H:%M')}</span>
                    <span style='color: var(--text-muted); font-size: 0.875rem;'>#{len(st.session_state.conversation_history) - i}</span>
                </div>
                <div class='activity-query'>
                    <strong>💬 Query:</strong> {item['query']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='custom-alert alert-info'>No recent activity to display.</div>", unsafe_allow_html=True)
    
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