from agents.ollama_client import OllamaClient

SYSTEM_PROMPT = """
You are a conversation router for a smart social network. Classify merchant messages as one of: 'partnership_request', 'moderation', or 'fallback'. Always respond with only the classification label.
"""

class RouterAgent:
    """
    Classifies merchant messages and determines which agent should handle them.
    """
    def __init__(self):
        self.llm = OllamaClient()

    def classify(self, message: str) -> str:
        prompt = f"{SYSTEM_PROMPT}\nMessage: {message}\nClassification:"
        result = self.llm.generate(prompt)
        return result.strip().split()[0].lower()  # Always return the first word as label 