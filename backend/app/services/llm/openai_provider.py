from openai import AsyncOpenAI
from typing import Dict, Any
import json
from app.services.llm.provider import LLMProvider
from config.settings import settings


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider implementation."""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text using OpenAI."""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output."""
        
        structured_prompt = f"""{prompt}

Return your response as a valid JSON object matching this schema:
{json.dumps(schema, indent=2)}

Only return the JSON, no additional text.
"""
        
        response = await self.generate(structured_prompt, temperature=0.3)
        
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception:
            return {}
        
        return {}
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            response = await self.generate("Hello", max_tokens=5)
            return bool(response)
        except Exception:
            return False
