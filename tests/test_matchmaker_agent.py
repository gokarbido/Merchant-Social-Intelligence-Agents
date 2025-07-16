import pandas as pd
import os
import tempfile
import pytest
from agents.matchmaker_agent import MatchmakerAgent

MERCHANT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fake_merchant_dataset.csv'))

@pytest.fixture
def agent():
    return MatchmakerAgent(MERCHANT_DATA_PATH)

def test_find_matches(agent):
    matches = agent.find_matches("123", "Tem alguém que faz doces para festas na zona leste?")
    assert isinstance(matches, list) 