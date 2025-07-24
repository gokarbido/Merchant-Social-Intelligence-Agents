import os
import sys
import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import FastAPI

# This will be handled by conftest.py
from api.main import app

client = TestClient(app)

def test_e2e_social_media_promotion():
    response = client.post(
        "/message", 
        json={"message": "Preciso de ajuda com divulgação no Instagram", "user_id": "001"}
    )
    data = response.json()
    assert response.status_code == 200
    assert any(key in data for key in ["response", "source_agent_response", "agent_workflow"])
    assert "instagram" in data["response"].lower() or "redes sociais" in data["response"].lower()

def test_e2e_matchmaking():
    response = client.post(
        "/message", 
        json={"message": "Tem alguém que faz doces para festas na zona leste?", "user_id": "001"}
    )
    data = response.json()
    assert response.status_code == 200
    assert any(key in data for key in ["response", "source_agent_response", "agent_workflow"])

def test_e2e_moderation():
    response = client.post(
        "/message", 
        json={"message": "Conteúdo ofensivo que deve ser bloqueado", "user_id": "001"}
    )
    data = response.json()
    assert response.status_code == 200
    # Check if either ModeratorAgent was involved or if the message was flagged in workflow
    assert any(
        step.get("agent_name") == "ModeratorAgent" or 
        (step.get("moderation_action") == "flag" if "moderation_action" in step else False)
        for step in data.get("agent_workflow", [])
    )

def test_e2e_fallback():
    response = client.post(
        "/message", 
        json={"message": "Qual foi o último jogo do Palmeiras?", "user_id": "001"}
    )
    data = response.json()
    assert response.status_code == 200
    assert any(step.get("agent_name") in ["HumanEscalationAgent", "ModeratorAgent"] 
              for step in data.get("agent_workflow", []))

@pytest.mark.asyncio
async def test_e2e_mcp_with_metadata_and_history():
    payload = {
        "user_id": "001",
        "message": "quero divulgar promoções da minha loja",
        "metadata": {"source": "pytest", "test_case": "mcp_with_metadata"},
        "history": [
            {"user_id": "001", "message": "tenho interesse em roupa masculina"},
            {"user_id": "001", "message": "quero vender mais"}
        ]
    }
    response = client.post("/mcp/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert all(key in data for key in ["response", "source_agent_response", "agent_workflow"])
    data = response.json()
    assert "response" in data
    assert "agent_workflow" in data 