"""
Wrapper around Google Gemini inference endpoint using google-genai SDK.
"""
import json
import logging
from typing import Any
from google import genai

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model_name
        self.client = genai.Client(api_key=key) if key else None

    async def _call_gemini(self, prompt: str, json_mode: bool = True) -> str:
        """Send a prompt to Gemini and return the raw text response."""
        if not self.client:
            logger.warning("Gemini API key not configured. Returning stub response.")
            return ""
            
        try:
            config = genai.types.GenerateContentConfig()
            if json_mode:
                config.response_mime_type = "application/json"
                
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini call failed (%s) — falling back to stub response.", exc)
            return ""

    async def extract_skills_from_text(self, text: str) -> list[dict[str, Any]]:
        """
        Extract technical, soft, digital-literacy, and industry-readiness skills
        from a CV or job description. Returns a list of {name, category} dicts.
        """
        prompt = (
            "You are a skills-extraction engine for a Nigerian graduate-employability "
            "platform. Read the text below and return ONLY a JSON array of objects "
            'like {"name": "...", "category": "technical|soft|digital_literacy|industry_readiness"}. '
            f"Text:\n{text}"
        )
        raw = await self._call_gemini(prompt)
        return self._safe_json_list(raw)

    async def generate_recommendations(self, graduate_profile: dict[str, Any], missing_skills: list[str]) -> list[dict[str, Any]]:
        """
        Generate personalized recommendations (courses, certifications, career advice)
        given a graduate's profile and their current missing skills.
        """
        prompt = (
            "You are a career advisor for Nigerian graduates. Given this graduate "
            f"profile: {json.dumps(graduate_profile)} and these missing skills: "
            f"{missing_skills}, return ONLY a JSON array of objects like "
            '{"category": "missing_skill|certification|course|career_advice|interview_prep", '
            '"title": "...", "detail": "..."}.'
        )
        raw = await self._call_gemini(prompt)
        return self._safe_json_list(raw)

    async def summarize_cv(self, cv_text: str) -> str:
        prompt = f"Summarize this CV in 3-4 sentences for a recruiter dashboard:\n{cv_text}"
        raw = await self._call_gemini(prompt, json_mode=False)
        return raw or "Summary unavailable — Gemini endpoint not reachable."

    @staticmethod
    def _safe_json_list(raw: str) -> list[dict[str, Any]]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            logger.warning("Gemini returned non-JSON output; ignoring.")
            return []


gemini_client = GeminiClient()
