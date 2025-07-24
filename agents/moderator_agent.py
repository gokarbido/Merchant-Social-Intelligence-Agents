from agents.ollama_client import OllamaClient

SYSTEM_PROMPT = """
You are a conversation moderator for a smart social network. Your role is to moderate merchant messages while allowing legitimate business-related discussions.

For messages that are clearly spam, scams, or abusive, respond with 'flag: [reason]'.
For very short or unclear messages that need more context, respond with 'warn: [reason]'.
For all other messages, especially those related to business services like social media marketing, respond with 'allow'.

Examples:
- "compre agora! oferta por tempo limitado!" -> flag: spam
- "oi" -> warn: message too short
- "preciso de ajuda com divulgação no instagram" -> allow
- "faço posts para redes sociais" -> allow
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