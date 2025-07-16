from agents.moderator_agent import ModeratorAgent
import pytest

@pytest.fixture
def agent():
    return ModeratorAgent()

def test_flag(agent):
    result = agent.moderate("abuso")
    assert result["action"] == "flag"
    assert result["reason"]

def test_warn(agent):
    result = agent.moderate("oi")
    assert result["action"] in ["warn", "allow"]

def test_allow(agent):
    result = agent.moderate("o usuário está ótimo e não contém linguagem ofensiva.")
    assert result["action"] == "allow" 