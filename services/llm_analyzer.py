"""
Service layer for evaluating Polish essays using Google Gemini LLM API.
"""

from abc import ABC, abstractmethod
import json
import logging
import os
from typing import Any, Optional
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMAnalysisError(Exception):
    """Raised when essay analysis fails due to API errors, missing configuration, or invalid JSON."""
    pass


class BaseEssayAnalyzer(ABC):
    """Abstract Base Class defining the contract for essay evaluation services."""

    @abstractmethod
    def analyze_essay(self, essay_content: str) -> dict[str, Any]:
        """
        Analyze a Polish essay and return structured evaluation feedback.

        :param essay_content: The text of the essay written in Polish.
        :return: Dict containing corrected_text, errors, and advanced_synonyms.
        :raises LLMAnalysisError: If evaluation fails.
        """
        pass


class LLMAnalyzer(BaseEssayAnalyzer):
    """
    LLM-powered essay analyzer using Google Generative AI (Gemini).
    Acts as a C1 level Polish language examiner.
    """

    SYSTEM_PROMPT: str = (
        "You are an expert C1 level Polish language examiner and university lecturer. "
        "Analyze the provided essay written in Polish for grammar, spelling, punctuation, sentence structure, and stylistic register. "
        "You MUST return ONLY a valid JSON object matching this exact structure without any extra text:\n"
        "{\n"
        '  "corrected_text": "string (the full essay text with all corrections applied)",\n'
        '  "errors": [\n'
        '    "string (detailed explanation of a specific grammatical, spelling, or stylistic mistake)"\n'
        '  ],\n'
        '  "advanced_synonyms": [\n'
        '    {\n'
        '      "original": "string (basic Polish word or phrase used in the essay)",\n'
        '      "suggestion": "string (advanced/academic C1-C2 synonym)",\n'
        '      "explanation": "string (brief context explaining why this synonym elevates the text)"\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash"
    ) -> None:
        """
        Initialize the Gemini LLM analyzer with API key and model selection.
        """
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = getattr(settings, "GOOGLE_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")

        self.model_name: str = model_name

        if self.api_key:
            genai.configure(api_key=self.api_key)

    def analyze_essay(self, essay_content: str) -> dict[str, Any]:
        """
        Analyze a Polish essay using Gemini LLM.

        :param essay_content: User submitted essay text.
        :return: Dictionary with keys 'corrected_text', 'errors', and 'advanced_synonyms'.
        :raises LLMAnalysisError: If content is empty, API key is missing, API fails, or response is invalid JSON.
        """
        if not essay_content or not essay_content.strip():
            raise LLMAnalysisError("Essay content cannot be empty.")

        if not self.api_key:
            raise LLMAnalysisError("Google API Key is missing. Please configure GOOGLE_API_KEY.")

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.SYSTEM_PROMPT
            )
            prompt: str = f"Analyze the following Polish essay:\n\n{essay_content}"

            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2
            )

            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            if not response or not hasattr(response, "text") or not response.text:
                raise LLMAnalysisError("Empty response received from Gemini API.")

            raw_text: str = response.text.strip()
            return self._parse_and_validate_response(raw_text)

        except Exception as exc:
            logger.error("LLM essay analysis failed: %s", str(exc))
            if isinstance(exc, LLMAnalysisError):
                raise exc
            raise LLMAnalysisError(f"Failed to evaluate essay via Gemini API: {str(exc)}") from exc

    def _parse_and_validate_response(self, raw_text: str) -> dict[str, Any]:
        """
        Parse raw text output into JSON and validate required schema keys.

        :param raw_text: Raw response string from LLM.
        :return: Validated JSON dict.
        :raises LLMAnalysisError: If JSON parsing fails or required keys are missing.
        """
        clean_text: str = raw_text
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            data: dict[str, Any] = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            raise LLMAnalysisError(f"Invalid JSON response from LLM: {str(exc)}") from exc

        required_keys = {"corrected_text", "errors", "advanced_synonyms"}
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise LLMAnalysisError(f"LLM response missing required JSON keys: {missing_keys}")

        if not isinstance(data["corrected_text"], str):
            data["corrected_text"] = str(data["corrected_text"])

        if not isinstance(data["errors"], list):
            data["errors"] = [str(data["errors"])]

        if not isinstance(data["advanced_synonyms"], list):
            data["advanced_synonyms"] = []

        return data
