from agents.ollama_client import OllamaClient

SYSTEM_PROMPT = """
You are a conversation moderator for a smart social network. Moderate merchant messages. Respond with one of: 'flag', 'warn', or 'allow'. If flag or warn, provide a short reason after the label. Example: 'flag: spam content'.
"""

class ModeratorAgent:
    """
    Analyzes messages for spam, inappropriate content, or low-quality interactions.
    """
    def __init__(self):
        self.llm = OllamaClient()

    def moderate(self, message: str) -> dict:
        prompt = f"{SYSTEM_PROMPT}\nMessage: {message}\nModeration:"
        result = self.llm.generate(prompt).strip().lower()
        if result.startswith("flag"):
            reason = result[4:].strip(": ") or "inappropriate or abusive content"
            return {"action": "flag", "reason": reason}
        elif result.startswith("warn"):
            reason = result[4:].strip(": ") or "message too short"
            return {"action": "warn", "reason": reason}
        elif result.startswith("allow"):
            return {"action": "allow"}
        else:
            return {"action": "allow"}  # Default to allow if unclear 