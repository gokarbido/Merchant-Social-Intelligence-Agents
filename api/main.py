from fastapi import FastAPI, Request, WebSocket
from pydantic import BaseModel
from agents.router_agent import RouterAgent
from agents.matchmaker_agent import MatchmakerAgent
from agents.moderator_agent import ModeratorAgent
from typing import List, Dict, Optional, Any
import os
from agents.orchestrator import AgentOrchestrator, AgentInput

app = FastAPI()

# Path to merchant dataset (fixed for Docker)
MERCHANT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fake_merchant_dataset.csv'))

# Initialize agents
router_agent = RouterAgent()
matchmaker_agent = MatchmakerAgent(MERCHANT_DATA_PATH)
moderator_agent = ModeratorAgent()

# Initialize orchestrator
orchestrator = AgentOrchestrator(MERCHANT_DATA_PATH)

class MessageRequest(BaseModel):
    message: str
    user_id: str
    feedback: str = None  # thumbs-up or thumbs-down

class AgentStep(BaseModel):
    agent_name: str
    classification: str = None
    matches: List[str] = None
    moderation_action: str = None
    moderation_reason: str = None

# Define Model Context Protocol (MCP) schema
class ModelContextProtocol(BaseModel):
    user_id: str
    message: str
    feedback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = None

@app.post("/message")
def process_message(payload: MessageRequest):
    agent_input = AgentInput(message=payload.message, user_id=payload.user_id, feedback=payload.feedback)
    agent_output = orchestrator.run(agent_input)
    return agent_output.dict()

@app.post("/mcp/message")
def mcp_message(payload: ModelContextProtocol):
    # Pass the MCP context to the orchestrator, using only the fields it currently supports
    agent_input = AgentInput(
        message=payload.message,
        user_id=payload.user_id,
        feedback=payload.feedback
    )
    # Optionally, you can extend AgentInput and the orchestrator to use metadata/history
    agent_output = orchestrator.run(agent_input)
    return agent_output.dict()

@app.get("/mcp/status")
def mcp_status():
    return {
        "status": "ok",
        "agents": ["router", "moderator", "matchmaker", "human_escalation"],
        "message": "MCP server is running. Human Escalation Agent is available for complex or high-risk cases.",
        "feedback_memory": orchestrator.feedback_memory
    }

# Optional: WebSocket endpoint for real-time agent workflow (not implemented)
# @app.websocket("/mcp/stream")
# async def mcp_stream(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text("MCP streaming not implemented yet.")
#     await websocket.close() 