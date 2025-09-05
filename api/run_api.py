#!/usr/bin/env python3
"""
Startup script for the Healthcare Scheduling System API.
"""

import uvicorn
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🏥 Starting Healthcare Scheduling System API...")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Alternative docs at: http://localhost:8000/redoc")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    print("❤️  Health check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
