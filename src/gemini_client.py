import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("gemini_client")

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI Client with provided API key.")
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client: {e}. Fallback engine active.")

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """
        Sends prompt to Gemini API to return structured JSON.
        If no API key or network error, returns None (caller will handle or fallback).
        """
        if self.client:
            try:
                full_prompt = f"{system_instruction}\n\nTask:\n{prompt}\n\nIMPORTANT: Return ONLY valid JSON format."
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config={'response_mime_type': 'application/json'}
                )
                if response and response.text:
                    return json.loads(response.text)
            except Exception as e:
                logger.error(f"Gemini API generation error: {e}")
        return None
