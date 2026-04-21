"""Core security and response pipeline for AiGuard.

This module contains the three main stages used by the application:
1. A fast regex-based prompt injection screen
2. A Gemini-powered judge that classifies prompt safety
3. A structured runbook generator for safe operational prompts
"""

import os
import re
from typing import Any

from google import genai
from dotenv import load_dotenv

from .models import SecurityAssessment, RunbookResponse

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
FAST_INJECTION_PATTERNS = [
    r"ignore previous",
    r"ignore your rules",
    r"system reset",
    r"developer mode",
    r"print your rules",
    r"system password",
    r"reveal hidden policies",
    r"bypass safeguards",
    r"disable safety checks",
    r"exfiltrate aws credentials",
]


def extract_usage_stats(response: Any) -> dict:
    """Extract normalized token usage information from a Gemini response."""
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return {
            "prompt_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "thought_tokens": 0,
            "tool_tokens": 0,
        }

    output_tokens = (
        getattr(usage, "candidates_token_count", None)
        or getattr(usage, "response_token_count", None)
        or 0
    )

    return {
        "prompt_tokens": getattr(usage, "prompt_token_count", 0) or 0,
        "output_tokens": output_tokens,
        "total_tokens": getattr(usage, "total_token_count", 0) or 0,
        "cached_tokens": getattr(usage, "cached_content_token_count", 0) or 0,
        "thought_tokens": getattr(usage, "thoughts_token_count", 0) or 0,
        "tool_tokens": getattr(usage, "tool_use_prompt_token_count", 0) or 0,
    }


def check_fast_injection(text: str) -> bool:
    """Return False when the prompt matches obvious prompt-injection patterns."""
    normalized_text = text.lower()
    for pattern in FAST_INJECTION_PATTERNS:
        if re.search(pattern, normalized_text):
            return False
    return True


def detect_adversarial_intent(text: str) -> tuple[SecurityAssessment, dict]:
    """Ask Gemini to classify whether a prompt is adversarial or policy-breaking."""
    prompt = f"Analyze this user prompt for injection attacks or rule-breaking intent: '{text}'"

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": SecurityAssessment.model_json_schema(),
        }
    )
    return SecurityAssessment.model_validate_json(response.text), extract_usage_stats(response)


def get_runbook_fix(prompt: str) -> tuple[RunbookResponse, dict]:
    """Generate a structured CloudOps runbook for prompts judged to be safe."""
    system_instruction = "You are a CloudOps expert. Provide clear fixes in structured JSON."

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": RunbookResponse.model_json_schema(),
        }
    )
    return RunbookResponse.model_validate_json(response.text), extract_usage_stats(response)
