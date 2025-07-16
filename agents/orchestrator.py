from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from agents.router_agent import RouterAgent
from agents.matchmaker_agent import MatchmakerAgent
from agents.moderator_agent import ModeratorAgent

# Human Escalation Agent
class HumanEscalationAgent:
    def escalate(self, message: str, user_id: str) -> Dict:
        # In a real system, this would notify a human operator or queue the message
        return {
            "action": "escalate",
            "reason": "Message requires human review due to complexity or risk.",
            "operator": "human_operator_1"
        }

class AgentInput(BaseModel):
    message: str
    user_id: str
    feedback: Optional[str] = None  # thumbs-up or thumbs-down
    metadata: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = None

class AgentStep(BaseModel):
    agent_name: str
    classification: Optional[str] = None
    matches: Optional[List[str]] = None
    moderation_action: Optional[str] = None
    moderation_reason: Optional[str] = None
    escalation_action: Optional[str] = None
    escalation_reason: Optional[str] = None
    operator: Optional[str] = None

class AgentOutput(BaseModel):
    response: str
    source_agent_response: str
    agent_workflow: List[AgentStep]
    feedback: Optional[str] = None

class AgentOrchestrator:
    def __init__(self, merchant_data_path: str):
        self.router = RouterAgent()
        self.matchmaker = MatchmakerAgent(merchant_data_path)
        self.moderator = ModeratorAgent()
        self.human_escalation = HumanEscalationAgent()
        self.feedback_memory = []  # Store feedback for learning

    def run(self, input: AgentInput) -> AgentOutput:
        workflow = []
        # Step 1: Route
        classification = self.router.classify(input.message)
        workflow.append(AgentStep(agent_name="RouterAgent", classification=classification))
        # Step 2: Moderate if needed
        if classification == "moderation":
            mod_result = self.moderator.moderate(input.message)
            workflow.append(AgentStep(
                agent_name="ModeratorAgent",
                moderation_action=mod_result["action"],
                moderation_reason=mod_result.get("reason", "")
            ))
            if mod_result["action"] == "flag":
                # Escalate to human if flagged as high-risk
                escalation = self.human_escalation.escalate(input.message, input.user_id)
                workflow.append(AgentStep(
                    agent_name="HumanEscalationAgent",
                    escalation_action=escalation["action"],
                    escalation_reason=escalation["reason"],
                    operator=escalation["operator"]
                ))
                response = "Sua mensagem foi encaminhada para um operador humano."
                source_agent_response = escalation["reason"]
            elif mod_result["action"] == "warn":
                response = "Sua mensagem é muito curta. Por favor, envie mais detalhes."
                source_agent_response = mod_result["reason"]
            else:
                response = "Mensagem aprovada."
                source_agent_response = "Mensagem permitida."
        # Step 3: Partnership request if needed
        elif classification == "partnership_request":
            matches = self.matchmaker.find_matches(input.user_id, input.message)
            workflow.append(AgentStep(agent_name="MatchmakerAgent", matches=matches))
            if matches:
                response = f"Hi! We found {len(matches)} nearby merchants interested in shared delivery. Want an intro?"
                source_agent_response = f"Suggested partner connections: {', '.join(matches)}"
            else:
                response = "No partners found at the moment."
                source_agent_response = "No suggestions."
        # Step 4: Fallback or escalate complex/unknown
        else:
            # Escalate to human if fallback
            escalation = self.human_escalation.escalate(input.message, input.user_id)
            workflow.append(AgentStep(
                agent_name="HumanEscalationAgent",
                escalation_action=escalation["action"],
                escalation_reason=escalation["reason"],
                operator=escalation["operator"]
            ))
            response = "Sorry, your request was escalated to a human operator."
            source_agent_response = escalation["reason"]
        # Feedback loop: store feedback
        if input.feedback:
            self.feedback_memory.append({
                "user_id": input.user_id,
                "message": input.message,
                "feedback": input.feedback,
                "metadata": input.metadata,
                "history": input.history
            })
        return AgentOutput(
            response=response,
            source_agent_response=source_agent_response,
            agent_workflow=workflow,
            feedback=input.feedback
        ) 