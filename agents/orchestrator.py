from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from agents.router_agent import RouterAgent
from agents.matchmaker_agent import MatchmakerAgent
from agents.moderator_agent import ModeratorAgent
import os

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

class MatchInfo(BaseModel):
    id: str
    name: str
    city: str
    message: str

class AgentStep(BaseModel):
    agent_name: str
    classification: Optional[str] = None
    matches: Optional[List[MatchInfo]] = None
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
        self.matchmaker = MatchmakerAgent(merchant_data_path, os.environ.get("PGVECTOR_DSN"))
        self.moderator = ModeratorAgent()
        self.human_escalation = HumanEscalationAgent()
        self.feedback_memory = []  # Store feedback for learning

    async def run(self, input: AgentInput) -> AgentOutput:
        """Process the input through the agent workflow."""
        workflow = []
        response = ""
        source_agent_response = ""
        classification = None
        
        # Step 1: Route the message
        classification = self.router.classify(input.message)
        workflow.append(AgentStep(agent_name="RouterAgent", classification=classification))
        
        # Step 2: Check for moderation needs
        mod_result = self.moderator.moderate(input.message)
        if mod_result["action"] != "allow":
            workflow.append(AgentStep(agent_name="ModeratorAgent", 
                                   moderation_action=mod_result["action"],
                                   moderation_reason=mod_result["reason"]))
            
            if mod_result["action"] == "escalate":
                # Escalate to human
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
            matches = await self.matchmaker.find_matches(input.user_id, input.message, self.feedback_memory)
            if matches:
                workflow.append(AgentStep(agent_name="MatchmakerAgent", matches=matches))
                # Format the matches with their details
                match_descriptions = []
                for match in matches:
                    city_info = f" ({match['city']})" if match.get('city') else ""
                    match_desc = f"{match.get('name', 'Comerciante')}{city_info}: \"{match.get('message', '')}\""
                    match_descriptions.append(match_desc)
                
                response = (
                    f"Encontrei {len(matches)} parceiros em potencial que podem te ajudar:\n\n"
                    f"- " + "\n\n- ".join(match_descriptions) + "\n\n"
                    "Você gostaria que eu os conecte com você?"
                )
                match_ids = [m.get('id', '') for m in matches]
                source_agent_response = f"Suggested partner connections: {', '.join(match_ids)}"
            else:
                workflow.append(AgentStep(agent_name="MatchmakerAgent", matches=[]))
                response = "No momento não encontrei parceiros disponíveis, mas posso te avisar quando surgir alguém."
                source_agent_response = "No suggestions."
        # Step 4: Handle service requests (including social media promotion)
        elif classification in ["service_request", "social_media_promotion"]:
            # Prepare base response based on service type
            if classification == "social_media_promotion":
                base_response = (
                    "Entendi que você precisa de ajuda com promoção nas redes sociais! "
                    "Aqui estão algumas dicas para melhorar sua presença no Instagram:\n"
                    "1. Poste conteúdo de qualidade regularmente\n"
                    "2. Use hashtags relevantes\n"
                    "3. Interaja com outros perfis do seu nicho\n\n"
                )
            else:
                base_response = ""
                
            # Use matchmaker to find relevant connections for any service request
            matches = await self.matchmaker.find_matches(input.user_id, input.message, self.feedback_memory)
            
            if matches:
                workflow.append(AgentStep(agent_name="MatchmakerAgent", matches=matches))
                match_list = "\n".join([
                    f"- {m.get('name', 'Alguém')} ({m.get('city', '')}): {m.get('message', '')}"
                    for m in matches[:3]  # Show top 3 matches
                ])
                response = (
                    f"{base_response}"
                    f"Encontrei alguns parceiros que podem te ajudar:\n"
                    f"{match_list}\n\n"
                    f"Gostaria que eu os conecte com você?"
                )
                source_agent_response = f"Found {len(matches)} potential service providers"
            else:
                workflow.append(AgentStep(agent_name="MatchmakerAgent", matches=[]))
                response = (
                    f"{base_response}"
                    "No momento não encontrei parceiros disponíveis, mas posso te avisar quando surgir alguém. "
                    "Posso te ajudar com mais alguma coisa?"
                )
                source_agent_response = "No service providers found"
        # Step 5: Fallback or escalate complex/unknown
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