from agents.ollama_client import OllamaClient

SYSTEM_PROMPT = """
You are a conversation router for a merchant social network. Classify merchant messages into one of these categories:
- 'partnership_request': Requests for business partnerships, collaborations, or joint ventures
- 'social_media_promotion': Requests for help with social media marketing, Instagram, Facebook, or other platform promotion
- 'service_request': Other requests for services, help, or information
- 'moderation': Inappropriate, abusive, or spam content that needs moderation
- 'fallback': Only use if the message doesn't fit any other category

Examples:
- "preciso de ajuda com divulgação no insta" -> social_media_promotion
- "quero aumentar meus seguidores" -> social_media_promotion
- "preciso de um fornecedor" -> partnership_request
- "como faço para vender mais?" -> service_request
- "seu lixo" -> moderation

Respond with only the classification label in lowercase.
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