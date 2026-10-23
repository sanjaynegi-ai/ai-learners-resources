from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

TicketId = Annotated[str, StringConstraints(pattern=r"^QC-[0-9]{3,8}$")]
Tag = Annotated[str, StringConstraints(min_length=1, max_length=40, pattern=r"^[a-z][a-z0-9-]*$")]
Category = Literal["billing", "shipping", "returns", "other"]


class TicketIn(BaseModel):
    """External request body. Strict: no coercion of True/"10" to int; unknown fields rejected."""
    model_config = ConfigDict(strict=True, extra="forbid")

    ticket_id: TicketId
    amount: int = Field(ge=0, le=1_000_000, description="Synthetic currency units")
    tags: list[Tag] = Field(default_factory=list, max_length=10)


class Ticket(BaseModel):
    """Stored and returned representation. Tenant is deliberately not echoed to clients."""
    model_config = ConfigDict(frozen=True)

    ticket_id: str
    amount: int
    tags: tuple[str, ...]
    status: Literal["open", "triaged"] = "open"
    category: Category | None = None
