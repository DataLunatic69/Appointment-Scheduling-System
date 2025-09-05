"""
FastAPI application for Healthcare Scheduling System API.
Provides REST endpoints for interacting with the supervisor agent.
"""

import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage

from api.models import (
    ChatRequest, ChatResponse, HealthResponse, ErrorResponse, 
    SystemStatusResponse, AgentInfo
)
from utils.logging_config import setup_logging, get_logger, log_agent_operation, log_error_with_context

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Scheduling System API",
    description="REST API for AI-powered healthcare scheduling with multi-agent system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for supervisor and session management
supervisor = None
start_time = time.time()
active_threads: Dict[str, Dict[str, Any]] = {}

# Agent information
AGENT_INFO = {
    "patient_agent": {
        "name": "Patient Management Agent",
        "description": "Handles patient information, creation, updates, and searches",
        "tools": ["get_patient_info", "update_patient_info", "create_patient", "search_patients"],
        "status": "active"
    },
    "scheduling_agent": {
        "name": "Scheduling Agent", 
        "description": "Manages appointment scheduling, availability, and rescheduling",
        "tools": ["get_doctor_schedule", "check_availability", "schedule_appointment", "reschedule_appointment", "cancel_appointment", "get_appointments"],
        "status": "active"
    },
    "insurance_agent": {
        "name": "Insurance Verification Agent",
        "description": "Handles insurance verification, coverage checks, and copay information",
        "tools": ["verify_insurance", "check_coverage", "get_copay_info"],
        "status": "active"
    },
    "communication_agent": {
        "name": "Communication Agent",
        "description": "Manages email communications, reminders, and follow-ups",
        "tools": ["send_appointment_reminder", "send_followup", "send_intake_form"],
        "status": "active"
    },
    "data_export_agent": {
        "name": "Data Export Agent",
        "description": "Generates reports, exports data, and creates analytics",
        "tools": ["generate_daily_schedule", "generate_patient_report", "export_appointments"],
        "status": "active"
    },
    "supervisor": {
        "name": "Supervisor Agent",
        "description": "Coordinates between all agents and handles complex queries",
        "tools": ["route_to_agent", "coordinate_agents", "handle_complex_queries"],
        "status": "active"
    }
}


def get_supervisor():
    """Dependency to get the supervisor agent instance."""
    global supervisor
    if supervisor is None:
        try:
            from agents.supervisor import supervisor as supervisor_instance
            supervisor = supervisor_instance
            logger.info("Supervisor agent loaded successfully")
        except Exception as e:
            log_error_with_context("Failed to load supervisor agent", e)
            raise HTTPException(status_code=500, detail="Supervisor agent not available")
    return supervisor


def get_or_create_thread(thread_id: str = None) -> str:
    """Get existing thread or create new one."""
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    if thread_id not in active_threads:
        active_threads[thread_id] = {
            "created_at": datetime.now(),
            "message_count": 0,
            "last_activity": datetime.now()
        }
    
    return thread_id


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Healthcare Scheduling System API")
    try:
        # Initialize supervisor
        get_supervisor()
        logger.info("API startup completed successfully")
    except Exception as e:
        log_error_with_context("Failed to initialize API", e)
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic health information."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_available=list(AGENT_INFO.keys())
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_available=list(AGENT_INFO.keys())
    )


@app.get("/status", response_model=SystemStatusResponse)
async def system_status():
    """Get detailed system status."""
    uptime = time.time() - start_time
    
    agents = [
        AgentInfo(
            name=info["name"],
            description=info["description"],
            tools=info["tools"],
            status=info["status"]
        )
        for info in AGENT_INFO.values()
    ]
    
    return SystemStatusResponse(
        status="operational",
        agents=agents,
        uptime=uptime,
        last_updated=datetime.now()
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    supervisor_instance = Depends(get_supervisor)
):
    """
    Main chat endpoint for interacting with the supervisor agent.
    
    This endpoint processes user messages and returns responses from the AI system.
    """
    start_time = time.time()
    thread_id = get_or_create_thread(request.thread_id)
    
    try:
        # Log the incoming request
        logger.info(f"Processing chat request for thread {thread_id[:8]}...")
        log_agent_operation(
            "chat_request_received",
            {
                "thread_id": thread_id,
                "message_length": len(request.message),
                "include_metadata": request.include_metadata
            }
        )
        
        # Create config with thread_id for the checkpointer
        config = {"configurable": {"thread_id": thread_id}}
        
        # Process the query with the supervisor agent
        response = supervisor_instance.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )
        
        # Extract the final response
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            if messages and hasattr(messages[-1], 'content'):
                assistant_response = messages[-1].content
            else:
                assistant_response = "I apologize, but I couldn't generate a proper response. Please try again."
        else:
            assistant_response = str(response) if response else "I apologize, but I couldn't generate a proper response. Please try again."
        
        processing_time = time.time() - start_time
        
        # Update thread activity
        active_threads[thread_id]["message_count"] += 1
        active_threads[thread_id]["last_activity"] = datetime.now()
        
        # Log successful response
        logger.info(f"Chat request processed successfully in {processing_time:.2f}s")
        log_agent_operation(
            "chat_response_generated",
            {
                "thread_id": thread_id,
                "processing_time": processing_time,
                "response_length": len(assistant_response)
            }
        )
        
        # Prepare response data
        response_data = {
            "response": assistant_response,
            "thread_id": thread_id,
            "processing_time": processing_time
        }
        
        # Add metadata if requested
        if request.include_metadata:
            response_data["metadata"] = {
                "agent_used": "supervisor",
                "message_count": active_threads[thread_id]["message_count"],
                "thread_created": active_threads[thread_id]["created_at"].isoformat(),
                "last_activity": active_threads[thread_id]["last_activity"].isoformat()
            }
        
        return ChatResponse(**response_data)
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error processing request: {str(e)}"
        
        log_error_with_context(
            "Chat request processing failed",
            e,
            {
                "thread_id": thread_id,
                "processing_time": processing_time,
                "message": request.message
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@app.get("/threads/{thread_id}")
async def get_thread_info(thread_id: str):
    """Get information about a specific conversation thread."""
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread_info = active_threads[thread_id]
    return {
        "thread_id": thread_id,
        "created_at": thread_info["created_at"],
        "message_count": thread_info["message_count"],
        "last_activity": thread_info["last_activity"]
    }


@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a conversation thread."""
    if thread_id not in active_threads:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    del active_threads[thread_id]
    logger.info(f"Thread {thread_id[:8]}... deleted")
    
    return {"message": "Thread deleted successfully"}


@app.get("/threads")
async def list_threads():
    """List all active conversation threads."""
    return {
        "threads": [
            {
                "thread_id": tid,
                "created_at": info["created_at"],
                "message_count": info["message_count"],
                "last_activity": info["last_activity"]
            }
            for tid, info in active_threads.items()
        ],
        "total_threads": len(active_threads)
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    log_error_with_context("Unhandled exception in API", exc)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"exception": str(exc)}
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
