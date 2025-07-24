import pytest

# This will be handled by conftest.py
from agents.router_agent import RouterAgent

@pytest.fixture
def agent():
    return RouterAgent()

def test_matchmaking(agent):
    result = agent.classify("Quero dividir frete para entregas em Campinas. Quem topa?")
    assert result in ["partnership_request", "service_request"]

def test_moderation(agent):
    result = agent.classify("Eu tô cansado de receber pedido de negócios. Tem como bloquear isso?")
    assert result in ["moderation", "service_request"]

def test_social_media_promotion(agent):
    result = agent.classify("Preciso de ajuda com divulgação no instagram")
    assert result == "social_media_promotion"

def test_fallback(agent):
    result = agent.classify("Qual foi o último jogo do Palmeiras?")
    assert result in ["fallback", "service_request"]