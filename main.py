from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
import os
import uvicorn

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = BASE_DIR  # Parent directory containing multi_tool_agent
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*", "http://192.168.0.102:8989"]
SERVE_WEB_INTERFACE = True
SESSION_DB_URL = os.environ.get("SESSION_DB_URL", "sqlite:///./sessions.db")

app: FastAPI = get_fast_api_app(
    agent_dir=BASE_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE)

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host=os.environ.get("HOST", "192.168.0.102"), port=int(os.environ.get("PORT", 8989)))