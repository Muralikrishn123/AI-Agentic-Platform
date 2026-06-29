import google.generativeai as genai
from typing import Dict, Any
from app.services.llm.provider import LLMProvider
from config.settings import settings
import json
import asyncio


class GeminiProvider(LLMProvider):
    """Gemini LLM Provider implementation (compatible with google-generativeai >=0.7)."""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=settings.GEMINI_API_KEY, transport="rest")
        
        # Set primary model and fallbacks
        # gemini-2.5-flash is first since it has active quota on key_in_env_now
        self.model_name = 'gemini-2.5-flash'
        self.models_list = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash']
        self.model = genai.GenerativeModel(self.model_name)
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text using Gemini, with auto-retry, backoff, and model fallback for quota rate limits."""
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
        
        loop = asyncio.get_event_loop()
        
        last_exception = None
        for current_model_name in self.models_list:
            model_instance = genai.GenerativeModel(current_model_name)
            
            # Robust retry loop for 429 rate limit exceptions on the current model
            max_attempts = 3
            backoff_seconds = 4.0
            
            for attempt in range(1, max_attempts + 1):
                try:
                    response = await loop.run_in_executor(
                        None,
                        lambda m=model_instance: m.generate_content(
                            prompt,
                            generation_config=generation_config
                        )
                    )
                    return response.text
                except Exception as e:
                    err_msg = str(e).lower()
                    is_rate_limit = "429" in err_msg or "quota" in err_msg or "rate limit" in err_msg
                    is_daily_limit = "daily" in err_msg or "requestsperday" in err_msg or "limit: 20" in err_msg or "requests per day" in err_msg
                    
                    if is_daily_limit:
                        print(f"[Quota] Daily Gemini API quota exceeded ({current_model_name}). Trying fallback model...")
                        last_exception = e
                        break
                    
                    if is_rate_limit and attempt < max_attempts:
                        # Dynamically parse retryDelay if possible
                        import re
                        retry_match = re.search(r"retry in ([\d\.]+)s", err_msg)
                        if retry_match:
                            sleep_time = float(retry_match.group(1)) + 1.0
                            sleep_time = min(sleep_time, 10.0) # limit sleep to prevent timeout locks
                            print(f"[Backoff] Google requested backoff for {current_model_name}. Sleeping for {sleep_time}s...")
                        else:
                            sleep_time = backoff_seconds * attempt
                            print(f"[Rate Limit] Gemini rate limit hit for {current_model_name}. Attempt {attempt}/{max_attempts}. Sleeping for {sleep_time}s...")
                        await asyncio.sleep(sleep_time)
                    else:
                        last_exception = e
                        print(f"[Error] Model {current_model_name} failed: {e}. Trying fallback...")
                        break # Break the attempt loop to try the next fallback model immediately
        
        if last_exception:
            raise last_exception
        raise ValueError("All configured Gemini models failed to generate content")


    
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
        """Check if Gemini API is accessible."""
        try:
            response = await self.generate("Hello", max_tokens=5)
            return bool(response)
        except Exception:
            return False
