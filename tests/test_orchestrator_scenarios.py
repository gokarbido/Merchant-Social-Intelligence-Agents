import pytest
import os
from agents.orchestrator import AgentOrchestrator, AgentInput

MERCHANT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fake_merchant_dataset.csv'))
orchestrator = AgentOrchestrator(MERCHANT_DATA_PATH)

def test_matchmaker_sweets():
    input = AgentInput(message="Tem alguém que faz doces para festas na zona leste?", user_id="123")
    output = orchestrator.run(input)
    # Accept partnership_request or escalation
    assert any(step.agent_name == "MatchmakerAgent" or step.agent_name == "HumanEscalationAgent" for step in output.agent_workflow)

def test_moderator_block():
    input = AgentInput(message="Eu tô cansado de receber pedido de negócios. Tem como bloquear isso?", user_id="134")
    output = orchestrator.run(input)
    assert any(step.agent_name == "ModeratorAgent" for step in output.agent_workflow)
    # Accept flag, warn, or allow
    assert any((getattr(step, "moderation_action", None) in ["flag", "warn", "allow"]) for step in output.agent_workflow if step.agent_name == "ModeratorAgent")

def test_matchmaker_freight():
    input = AgentInput(message="Quero dividir frete para entregas em Campinas. Quem topa?", user_id="345")
    output = orchestrator.run(input)
    assert any(step.agent_name == "MatchmakerAgent" or step.agent_name == "HumanEscalationAgent" for step in output.agent_workflow)

def test_fallback_palmeiras():
    input = AgentInput(message="Qual foi o último jogo do Palmeiras?", user_id="456")
    output = orchestrator.run(input)
    # Accept escalation or fallback
    assert any(step.agent_name == "HumanEscalationAgent" or step.agent_name == "ModeratorAgent" for step in output.agent_workflow) 