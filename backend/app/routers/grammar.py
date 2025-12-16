from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..config import get_settings
from ..openai_client import (
    build_grammar_system_prompt,
    build_grammar_user_prompt,
    get_openai_client,
    run_moderation,
)


router = APIRouter()
settings = get_settings()


class Score(BaseModel):
    grammar: int = Field(ge=0, le=100)
    vocabulary: int = Field(ge=0, le=100)
    fluency: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class IssueSpan(BaseModel):
    start: int
    end: int


class Issue(BaseModel):
    index: int
    span: IssueSpan
    issue_type: str
    explanation_zh: str
    suggestion: str


class GrammarFeedback(BaseModel):
    original: str
    minimal_correction: str
    natural_version: str
    issues: List[Issue]
    score: Score


class GrammarRequest(BaseModel):
    sentence: str = Field(..., description="User's English sentence.")
    task_type: str = Field(
        "quick_fix",
        description="Type of task, e.g. quick_fix | translate_duel | story_builder | boss",
    )
    extra_context: Dict[str, Any] | None = Field(
        default=None, description="Optional extra context like Chinese prompt, story ID, etc."
    )


@router.post("/check", response_model=GrammarFeedback)
async def check_grammar(payload: GrammarRequest) -> GrammarFeedback:
    """
    Grammar check endpoint used by multiple game modes.
    - Runs moderation first.
    - Calls OpenAI Responses API to get structured JSON feedback.
    """
    # 1) Safety check
    run_moderation(payload.sentence)

    # 2) Call OpenAI Responses API
    client = get_openai_client()

    system_prompt = build_grammar_system_prompt()
    user_prompt = build_grammar_user_prompt(
        sentence=payload.sentence,
        task_type=payload.task_type,
        extra_context=payload.extra_context,
    )

    response = client.responses.create(
        model=settings.openai_grammar_model,
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format={"type": "json_object"},
    )

    # 3) Extract JSON from Responses API
    content_block = response.output[0].content[0].text  # type: ignore[index]
    raw_json = content_block.parsed if hasattr(content_block, "parsed") else None

    if raw_json is None:
        # Fallback: try string then parse, but we keep it simple here.
        raise ValueError("Model did not return parsed JSON.")

    return GrammarFeedback.model_validate(raw_json)




