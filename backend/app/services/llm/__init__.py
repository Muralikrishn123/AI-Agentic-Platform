from app.services.llm.provider import LLMProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.openai_provider import OpenAIProvider
from config.settings import settings


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    This decouples the platform from specific LLM implementations.
    """
    
    # For Phase 1, use Gemini
    # Later, can switch based on environment or config
    
    if settings.GEMINI_API_KEY:
        return GeminiProvider()
    elif settings.OPENAI_API_KEY:
        return OpenAIProvider()
    else:
        raise ValueError("No LLM provider configured. Set GEMINI_API_KEY or OPENAI_API_KEY")


__all__ = ["LLMProvider", "GeminiProvider", "OpenAIProvider", "get_llm_provider"]
