import requests
import sys
import json

API_URL = "http://localhost:8000/mcp/message"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python mcp_client.py <user_id> <message> [feedback]")
        sys.exit(1)
    user_id = sys.argv[1]
    message = " ".join(sys.argv[2:])
    feedback = None
    metadata = None
    history = None
    # Optionally allow feedback as last argument
    if sys.argv[-2] != user_id:
        feedback = sys.argv[-1]
        message = " ".join(sys.argv[2:-1])
    # Optionally allow metadata and history as JSON arguments
    if '--metadata' in sys.argv:
        idx = sys.argv.index('--metadata')
        metadata = json.loads(sys.argv[idx + 1])
    if '--history' in sys.argv:
        idx = sys.argv.index('--history')
        history = json.loads(sys.argv[idx + 1])
    payload = {"user_id": user_id, "message": message}
    if feedback:
        payload["feedback"] = feedback
    if metadata:
        payload["metadata"] = metadata
    if history:
        payload["history"] = history
    try:
        resp = requests.post(API_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        print("Response:", data.get("response"))
        print("Source Agent Response:", data.get("source_agent_response"))
        print("Agent Workflow:")
        for step in data.get("agent_workflow", []):
            print("  -", step)
        if data.get("feedback"):
            print("Feedback:", data["feedback"])
    except requests.exceptions.RequestException as e:
        print("HTTP Error:", e)
    except Exception as e:
        print("Error decoding response:", e)
        print("Raw response:", getattr(resp, 'text', None)) 