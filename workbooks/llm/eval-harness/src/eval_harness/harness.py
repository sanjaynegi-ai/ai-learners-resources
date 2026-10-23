"""Run the real refund-draft pipeline over one split, score every case, and summarize with denominators.

Per-case scoring uses the answer key decided before evaluation, not the pipeline's own checks:
  correct    expected needs_agent -> got needs_agent; expected ready -> ready, right date, right language,
             no amount or claim the order does not support
  harmful    a ready draft that should not be sent: expected needs_agent, wrong date, an unsupported amount,
             or a claim that an unissued refund was issued. One harmful draft fails the critical gate.
"""
import hashlib
import json
import math
import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from refund_drafts.config import Settings
from refund_drafts.domain import Order, Records, Ticket
from refund_drafts.pipeline import draft_reply
from refund_drafts.prompt import load_instructions

from . import dataset
from .simulated_model import SimulatedModel

PRICE_PER_MILLION = {"input": 0.50, "output": 2.00}  # Hypothetical USD prices for cost arithmetic only
GERMAN_MARKERS = ("Ihre", "Ihr ", "Vielen", "Danke", "Rückerstattung", "Mitarbeiter")
AMOUNT = re.compile(r"\b\d+[.,]\d{2}\b")
INTEGER_DOLLARS = re.compile(r"\$\s*(\d+)\b(?![.,]\d)")  # Narrow CAL-04 regression, not a general currency parser.
HARNESS_FILES = ("dataset.py", "simulated_model.py", "harness.py")


def language_ok(text: str, language: str) -> bool:
    """Heuristic only: Devanagari for Hindi, German function words for German, neither for English."""
    devanagari = any("ऀ" <= ch <= "ॿ" for ch in text)
    german = any(marker in text for marker in GERMAN_MARKERS)
    return {"hi": devanagari, "de": german and not devanagari, "en": not devanagari and not german}[language]


def records_for(cases: list[dict]) -> Records:
    orders = {c["order"]["order_id"]: Order.model_validate(c["order"]) for c in cases}
    tickets = {c["case_id"]: Ticket(ticket_id=c["case_id"], order_id=c["order"]["order_id"], text=c["ticket_text"])
               for c in cases}
    policies = json.loads((Path(__import__("refund_drafts").__file__).resolve().parents[2] / "fixtures" / "policies.json")
                          .read_text(encoding="utf-8"))
    return Records(orders, tickets, policies)


def score(case: dict, outcome) -> dict:
    order, expect = case["order"], case["expect"]
    draft = outcome.draft
    row = {"case_id": case["case_id"], "language": case["language"], "category": case["category"], "expect": expect,
           "status": outcome.status, "reasons": outcome.reasons, "attempts": outcome.attempts,
           "tokens_in": outcome.input_tokens, "tokens_out": outcome.output_tokens}
    problems = []
    if outcome.status == "ready" and draft is not None:
        text = draft.reply_text
        used = draft.refund_date_used.isoformat() if draft.refund_date_used else None
        if expect == "needs_agent":
            problems.append("should_have_escalated")
        if used != order["expected_refund_date"]:
            problems.append("wrong_or_missing_date")
        amounts = [float(a.replace(",", ".")) for a in AMOUNT.findall(text)]
        amounts.extend(float(a) for a in INTEGER_DOLLARS.findall(text))
        if any(abs(amount - order["refund_amount"]) > 0.005 for amount in amounts):
            problems.append("unsupported_amount")
        if order["refund_status"] != "issued" and "issued" in text.lower():
            problems.append("claims_issued")
        row["harmful"] = bool(problems)
        row["wrong_language"] = not language_ok(text, case["language"])
        row["correct"] = expect == "ready" and not problems and not row["wrong_language"]
    else:
        row["harmful"] = False
        row["wrong_language"] = False
        row["correct"] = expect == "needs_agent" and outcome.status == "needs_agent"
    row["problems"] = problems
    return row


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if not n:
        return None
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)


def rate(k: int, n: int) -> dict:
    return {"k": k, "n": n, "value": round(k / n, 3) if n else None, "ci95": wilson(k, n)}


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    ready = [r for r in rows if r["status"] == "ready"]
    answerable = [r for r in rows if r["expect"] == "ready"]
    latencies = sorted(r["latency_s"] for r in rows)
    cost = sum(r["tokens_in"] * PRICE_PER_MILLION["input"] + r["tokens_out"] * PRICE_PER_MILLION["output"] for r in rows) / 1e6
    return {
        "cases": n,
        "correct": rate(sum(r["correct"] for r in rows), n),
        "harmful_ready": rate(sum(r["harmful"] for r in rows), len(ready)),
        "coverage": rate(sum(r["correct"] for r in answerable), len(answerable)),
        "unnecessary_escalation": rate(sum(r["status"] == "needs_agent" for r in answerable), len(answerable)),
        "wrong_language_ready": rate(sum(r["wrong_language"] for r in ready), len(ready)),
        "failed": rate(sum(r["status"] == "failed" for r in rows), n),
        "latency_s": {"p50": round(statistics.median(latencies), 2),
                      "p95": round(latencies[max(0, math.ceil(0.95 * n) - 1)], 2)},
        "cost_usd_per_1000": round(cost / n * 1000, 4),
        "provider_calls_per_case": round(sum(r["attempts"] for r in rows) / n, 2),
    }


def slices(rows: list[dict]) -> dict:
    out = {}
    for key in ("language", "category"):
        for value in sorted({r[key] for r in rows}):
            group = [r for r in rows if r[key] == value]
            out[f"{key}={value}"] = {"correct": rate(sum(r["correct"] for r in group), len(group)),
                                     "harmful": sum(r["harmful"] for r in group)}
    return out


def _sha(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()[:16]


@dataclass
class Run:
    manifest: dict
    summary: dict
    slices: dict
    rows: list[dict] = field(repr=False)


def run(prompt_version: str, split: str, settings: Settings | None = None) -> Run:
    data = dataset.load()
    cases = [c for c in data["cases"] if c["split"] == split]
    if not cases:
        raise ValueError(f"No cases in split {split!r}")
    settings = settings or Settings()
    model = SimulatedModel({c["case_id"]: c for c in cases})
    records = records_for(cases)
    rows = []
    for case in cases:
        outcome = draft_reply(case["case_id"], records, model, settings, prompt_version=prompt_version, sleep=lambda _: None)
        row = score(case, outcome)
        row["latency_s"] = round(model.latency_s.get(case["case_id"], 0.0), 3)
        rows.append(row)
    source = Path(__file__).resolve().parent
    manifest = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset_version": data["dataset_version"], "dataset_sha256": dataset.fingerprint(), "split": split,
        "prompt_version": prompt_version, "prompt_sha256": _sha(load_instructions(prompt_version)),
        "model": f"simulated:{prompt_version}", "pipeline": {"refund_drafts": metadata.version("refund-drafts"),
                                                             "max_attempts": settings.max_attempts,
                                                             "max_output_tokens": settings.max_output_tokens},
        "harness_sha256": _sha(b"".join((source / name).read_bytes() for name in HARNESS_FILES)),
        "prices_per_million_usd": PRICE_PER_MILLION,
    }
    return Run(manifest, summarize(rows), slices(rows), rows)
