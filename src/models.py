"""Pydantic schemas used by AiGuard for structured Gemini responses."""

from typing import List

from pydantic import BaseModel, Field


class SecurityAssessment(BaseModel):
    """Structured decision returned by the LLM-as-a-judge safety step."""

    is_safe: bool = Field(description="True if the prompt is benign, False if it contains injection or malicious intent.")
    risk_score: int = Field(description="Risk level from 1 (Safe) to 10 (Critical Injection).")
    reason: str = Field(description="Brief explanation of the security decision.")


class RunbookResponse(BaseModel):
    """Structured CloudOps troubleshooting output for safe prompts."""

    summary: str = Field(description="A brief summary of the troubleshooting steps.")
    commands: List[str] = Field(description="List of terminal commands to run.")
    confidence_score: float = Field(description="How confident the AI is in this solution (0.0 to 1.0).")
