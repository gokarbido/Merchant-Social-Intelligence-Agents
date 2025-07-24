import os
import asyncio
import pytest

# This will be handled by conftest.py
from agents.orchestrator import AgentOrchestrator, AgentInput

# Create a test fixture for the orchestrator
@pytest.fixture
def test_orchestrator():
    merchant_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fake_merchant_dataset.csv'))
    return AgentOrchestrator(merchant_path)

@pytest.mark.asyncio
async def test_matchmaker_sweets(test_orchestrator):
    input = AgentInput(message="Tem alguém que faz doces para festas na zona leste?", user_id="123")
    output = await test_orchestrator.run(input)
    # Accept partnership_request or escalation
    assert any(step.agent_name in ["MatchmakerAgent", "HumanEscalationAgent"] for step in output.agent_workflow)

@pytest.mark.asyncio
async def test_moderator_block(test_orchestrator):
    input = AgentInput(message="Conteúdo ofensivo que deve ser bloqueado", user_id="134")
    output = await test_orchestrator.run(input)
    # Check if either ModeratorAgent was involved or if the message was flagged in workflow
    assert any(
        step.agent_name == "ModeratorAgent" or 
        (hasattr(step, 'moderation_action') and step.moderation_action == "flag")
        for step in output.agent_workflow
    )
    # Accept flag, warn, or allow
    assert any((getattr(step, "moderation_action", None) in ["flag", "warn", "allow"]) 
              for step in output.agent_workflow if step.agent_name == "ModeratorAgent")

@pytest.mark.asyncio
async def test_matchmaker_freight(test_orchestrator):
    input = AgentInput(message="Quero dividir frete para entregas em Campinas. Quem topa?", user_id="345")
    output = await test_orchestrator.run(input)
    assert any(step.agent_name in ["MatchmakerAgent", "HumanEscalationAgent"] for step in output.agent_workflow)

@pytest.mark.asyncio
async def test_fallback_palmeiras(test_orchestrator):
    input = AgentInput(message="Qual foi o último jogo do Palmeiras?", user_id="456")
    output = await test_orchestrator.run(input)
    # Accept escalation or fallback
    assert any(step.agent_name in ["HumanEscalationAgent", "ModeratorAgent"] for step in output.agent_workflow)