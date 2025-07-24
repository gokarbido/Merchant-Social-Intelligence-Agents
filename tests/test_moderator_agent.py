import pytest

# This will be handled by conftest.py
from agents.moderator_agent import ModeratorAgent

@pytest.fixture
def agent():
    return ModeratorAgent()

def test_flag_spam(agent):
    result = agent.moderate("COMPRE AGORA! OFERTA POR TEMPO LIMITADO!")
    assert result["action"] == "flag"
    assert "spam" in result["reason"].lower()

def test_flag_abuse(agent):
    result = agent.moderate("conteúdo ofensivo e abusivo")
    assert result["action"] == "flag"
    assert result["reason"]

def test_warn_short_message(agent):
    result = agent.moderate("oi")
    assert result["action"] == "warn"
    assert "message too short" in result["reason"].lower()

def test_allow_business_message(agent):
    result = agent.moderate("preciso de ajuda com divulgação no instagram")
    assert result["action"] == "allow"

def test_allow_service_offer(agent):
    result = agent.moderate("faço posts para redes sociais")
    assert result["action"] == "allow"

def test_allow_detailed_message(agent):
    result = agent.moderate("Olá, gostaria de saber mais sobre os serviços de marketing digital oferecidos.")
    assert result["action"] == "allow"