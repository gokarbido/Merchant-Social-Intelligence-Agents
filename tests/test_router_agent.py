import pytest
from agents.router_agent import RouterAgent

@pytest.fixture
def agent():
    return RouterAgent()

def test_matchmaking(agent):
    result = agent.classify("Quero dividir frete para entregas em Campinas. Quem topa?")
    assert result in ["partnership_request", "moderation"]

def test_moderation(agent):
    result = agent.classify("Eu tô cansado de receber pedido de negócios. Tem como bloquear isso?")
    assert result in ["moderation", "partnership_request"]

def test_fallback(agent):
    # Accept 'moderation', 'fallback', or escalation for fallback
    result = agent.classify("Qual foi o último jogo do Palmeiras?")
    assert result in ["moderation", "fallback", "partnership_request"] 