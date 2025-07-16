from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.main import app

client = TestClient(app)

def test_e2e_matchmaking():
    response = client.post("/message", json={"message": "Tem alguém que faz doces para festas na zona leste?", "user_id": "001"})
    data = response.json()
    assert (
        "comerciantes" in data["response"]
        or "parceiro" in data["response"]
        or "escalated" in data["response"].lower()
        or "human operator" in data["response"].lower()
    )

def test_e2e_moderation():
    response = client.post("/message", json={"message": "Eu tô cansado de receber pedido de negócios. Tem como bloquear isso?", "user_id": "001"})
    data = response.json()
    assert (
        "sinalizada" in data["response"]
        or "curta" in data["response"]
        or "escalated" in data["response"].lower()
        or "human operator" in data["response"].lower()
        or "No partners found" in data["response"]
    )

def test_e2e_fallback():
    response = client.post("/message", json={"message": "Qual foi o último jogo do Palmeiras?", "user_id": "001"})
    data = response.json()
    assert (
        "Desculpe" in data["response"]
        or "não entendi" in data["response"]
        or "escalated" in data["response"].lower()
        or "human operator" in data["response"].lower()
    )

def test_e2e_mcp_with_metadata_and_history():
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
    data = response.json()
    assert "response" in data
    assert "agent_workflow" in data 