"""Synthetic QuickCart records. In production these come from systems of record, never from the model."""
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


class Order(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    order_id: str
    payment_method: Literal["card", "bank_transfer", "wallet"]
    refund_status: Literal["issued", "pending", "not_requested"]
    expected_refund_date: date | None
    refund_amount: float
    language: Literal["en", "de", "hi"]


class Ticket(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    ticket_id: str
    order_id: str
    text: str


@dataclass(frozen=True)
class Records:
    orders: dict[str, Order]
    tickets: dict[str, Ticket]
    policies: dict[str, str]


def load_records(directory: Path = FIXTURES) -> Records:
    orders = [Order.model_validate(item) for item in json.loads((directory / "orders.json").read_text(encoding="utf-8"))]
    tickets = [Ticket.model_validate(item) for item in json.loads((directory / "tickets.json").read_text(encoding="utf-8"))]
    policies = json.loads((directory / "policies.json").read_text(encoding="utf-8"))
    return Records({o.order_id: o for o in orders}, {t.ticket_id: t for t in tickets}, policies)
