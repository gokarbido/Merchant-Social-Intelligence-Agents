import os
import tempfile
import pytest
import asyncio
import pandas as pd

# This will be handled by conftest.py
from agents.matchmaker_agent import MatchmakerAgent

MERCHANT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fake_merchant_dataset.csv'))

@pytest.fixture
def agent():
    return MatchmakerAgent(MERCHANT_DATA_PATH)

@pytest.mark.asyncio
async def test_find_matches(agent):
    matches = await agent.find_matches("123", "Tem alguém que faz doces para festas na zona leste?")
    assert isinstance(matches, list)