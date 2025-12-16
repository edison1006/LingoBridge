from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from openai import OpenAI

from .config import get_settings


settings = get_settings()


def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=settings.openai_api_key)


def run_moderation(text: str) -> Dict[str, Any]:
    """
    Run OpenAI moderation on user input. Raise 400 if content is flagged.
    """
    client = get_openai_client()
    resp = client.moderations.create(
        model=settings.openai_moderation_model,
        input=text,
    )
    result = resp.results[0]
    if result.flagged:
        raise HTTPException(
            status_code=400,
            detail={"code": "content_flagged", "message": "Input violates safety policy."},
        )
    return result.to_dict()  # type: ignore[no-any-return]


def build_grammar_system_prompt() -> str:
    """
    System prompt for grammar correction tasks.
    """
    return (
        "You are an English learning assistant for Chinese learners. "
        "Your job is ONLY to check grammar, spelling, and word collocations, "
        "without changing the original meaning.\n\n"
        "For each input, you MUST produce a JSON object with this structure:\n"
        "{\n"
        '  "original": string,\n'
        '  "minimal_correction": string,\n'
        '  "natural_version": string,\n'
        '  "issues": [\n'
        "    {\n"
        '      "index": number,              // issue index starting from 1\n'
        '      "span": { "start": number, "end": number }, // character offsets in original\n'
        '      "issue_type": string,        // e.g. Grammar, Spelling, Collocation\n'
        '      "explanation_zh": string,    // Chinese explanation\n'
        '      "suggestion": string         // short suggestion in English\n'
        "    }\n"
        "  ],\n"
        '  "score": {\n'
        '    "grammar": number,   // 0-100\n'
        '    "vocabulary": number,// 0-100\n'
        '    "fluency": number,   // 0-100\n'
        '    "overall": number    // 0-100\n'
        "  }\n"
        "}\n\n"
        "Rules:\n"
        "- Keep meaning unchanged.\n"
        "- Provide BOTH a minimal correction and a more natural version.\n"
        "- Issues list can be empty if the sentence is already very good.\n"
        "- The response MUST be valid JSON, no comments, no extra text before or after."
    )


def build_grammar_user_prompt(
    sentence: str,
    task_type: str,
    extra_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build user prompt string for grammar-related tasks, with task_type hint.
    """
    ctx_lines: List[str] = [
        f"Task type: {task_type}",
        f"Sentence:\n{sentence}",
    ]
    if extra_context:
        ctx_lines.append("Extra context:")
        for k, v in extra_context.items():
            ctx_lines.append(f"- {k}: {v}")
    return "\n".join(ctx_lines)





