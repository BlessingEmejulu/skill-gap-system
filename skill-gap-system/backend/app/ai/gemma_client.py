"""
Thin wrapper around a Google Gemma inference endpoint (e.g. a local Ollama server
running `gemma2`, or any OpenAI/REST-compatible Gemma deployment).

Swap `_call_gemma` for your actual provider (Ollama, Vertex AI, HF Inference, etc.)
without touching any calling code — every route/service only imports GemmaClient.
"""
import json
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class GemmaClient:
    def __init__(self, api_url: str | None = None, model_name: str | None = None):
        self.api_url = api_url or settings.gemma_api_url
        self.model_name = model_name or settings.gemma_model_name

    async def _call_gemma(self, prompt: str, json_mode: bool = True) -> str:
        """Send a prompt to Gemma and return the raw text response."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json" if json_mode else None,
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemma call failed (%s) — falling back to stub response.", exc)
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
        raw = await self._call_gemma(prompt)
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
        raw = await self._call_gemma(prompt)
        return self._safe_json_list(raw)

    async def summarize_cv(self, cv_text: str) -> str:
        prompt = f"Summarize this CV in 3-4 sentences for a recruiter dashboard:\n{cv_text}"
        raw = await self._call_gemma(prompt, json_mode=False)
        return raw or "Summary unavailable — Gemma endpoint not reachable."

    @staticmethod
    def _safe_json_list(raw: str) -> list[dict[str, Any]]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            logger.warning("Gemma returned non-JSON output; ignoring.")
            return []


gemma_client = GemmaClient()
