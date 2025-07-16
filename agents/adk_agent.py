from google.adk.agents import Agent
from agents.orchestrator import AgentOrchestrator

# Path to your merchant dataset
MERCHANT_DATA_PATH = "data/fake_merchant_dataset.csv"

# Initialize your orchestrator
orchestrator = AgentOrchestrator(MERCHANT_DATA_PATH)

def orchestrate_agent(message: str, user_id: str) -> dict:
    # Use your orchestrator to process the message
    result = orchestrator.run(message=message, user_id=user_id)
    return result.dict()

root_agent = Agent(
    name="merchant_social_agent",
    model="llama3.2",  # Use llama3.2 as requested
    description="Routes merchant messages and orchestrates agent workflow.",
    instruction="You are a smart social network agent. Route, moderate, and matchmake as needed.",
    tools=[orchestrate_agent],
) 