"""The output contract, stated twice on purpose.

JSON_SCHEMA is sent to the provider so it constrains the format (strict structured output).
DraftOut re-validates on our side, because a provider-side schema is not a substitute for our own check,
and the fake provider (or another provider) may not enforce it at all.
"""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_NAME = "refund_reply_draft"
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "reply_text": {"type": "string", "description": "Draft reply for the agent to review, under 120 words."},
        "refund_date_used": {"type": ["string", "null"], "description": "YYYY-MM-DD date from <order> if mentioned, else null."},
        "needs_agent": {"type": "boolean", "description": "True when the facts needed to answer are missing."},
    },
    "required": ["reply_text", "refund_date_used", "needs_agent"],
    "additionalProperties": False,
}


class DraftOut(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    reply_text: str = Field(min_length=1, max_length=1200)
    refund_date_used: date | None
    needs_agent: bool

    @classmethod
    def from_json(cls, text: str) -> "DraftOut":
        # JSON mode lets strict validation accept "YYYY-MM-DD" strings for the date field.
        return cls.model_validate_json(text)
