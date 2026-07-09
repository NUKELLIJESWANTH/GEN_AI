import os
import json
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from config import GEMINI_API_KEY

logger = logging.getLogger("GeminiClient")

class GeminiClient:
    def __init__(self):
        # Retrieve key. Note that we never hardcode or expose keys.
        self.api_key = GEMINI_API_KEY if GEMINI_API_KEY else os.getenv("GEMINI_API_KEY", "")
        self.model_name = "gemini-3.5-flash"
        
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found in config or environment variables. AI operations will fail.")
            self.client = None
        else:
            try:
                # Initialize the brand new Google GenAI client
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Successfully initialized google-genai Client.")
            except Exception as e:
                logger.error(f"Error initializing google-genai client: {e}")
                self.client = None

    def generate_structured_listing(self, prompt: str, system_instruction: str = None) -> dict:
        """
        Sends a prompt to Gemini requesting a structured e-commerce product listing JSON.
        Includes safety extraction fallbacks.
        """
        if not self.client:
            raise ValueError("Gemini client is not initialized. Please configure a valid GEMINI_API_KEY in Settings > Secrets.")

        try:
            logger.info(f"Invoking Gemini Model: {self.model_name}")
            
            # Use modern google-genai Client API
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            )
            
            if system_instruction:
                config.system_instruction = system_instruction

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            response_text = response.text
            if not response_text:
                raise ValueError("Received empty response from Gemini API.")
                
            logger.info("Successfully retrieved content from Gemini. Parsing JSON...")
            return self._parse_json_response(response_text)
            
        except APIError as e:
            logger.error(f"Gemini API Error: {e}")
            raise RuntimeError(f"Gemini API returned an error: {e.message}")
        except Exception as e:
            logger.error(f"Error generating content via Gemini: {e}")
            raise e

    def _parse_json_response(self, text: str) -> dict:
        """
        Tries to parse the response as JSON. Strips markdown blocks if present.
        """
        cleaned = text.strip()
        
        # Strip markdown ```json / ``` wrappers if the model returned them despite the config
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse raw text as JSON: {e}. Raw content: {text[:500]}")
            # Try a regex-based search for anything between curly brackets as a last resort
            import re
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            raise ValueError("Gemini response was not valid JSON.")
