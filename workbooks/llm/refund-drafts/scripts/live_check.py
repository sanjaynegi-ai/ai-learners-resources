"""Separately triggered live check against a real provider. Makes PAID API calls; never run in CI or tests.

    $env:REFUND_DRAFTS_PROVIDER="openai"; $env:OPENAI_MODEL="<model from your account>"
    # OPENAI_API_KEY must already be set privately in this terminal.
    uv run python scripts/live_check.py --confirm-paid-calls

Writes results/live-<timestamp>.json with every outcome, the model reported by the API, token usage and
the prompt version. Five fixture tickets and up to three attempts each bound the number of calls to 15.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from refund_drafts.config import ConfigError, settings_from_env
from refund_drafts.domain import load_records
from refund_drafts.pipeline import draft_reply
from refund_drafts.providers import OpenAIProvider, make_openai_client

parser = argparse.ArgumentParser()
parser.add_argument("--confirm-paid-calls", action="store_true", help="Required: acknowledges real, billed API calls")
args = parser.parse_args()
if not args.confirm_paid_calls:
    sys.exit("Refusing to run: this makes paid API calls. Re-run with --confirm-paid-calls if you intend that.")
try:
    settings = settings_from_env()
except ConfigError as error:
    sys.exit(f"Configuration error: {error}")
if settings.provider != "openai":
    sys.exit("Set REFUND_DRAFTS_PROVIDER=openai for the live check; offline runs use the CLI.")

records = load_records()
provider = OpenAIProvider(make_openai_client(os.environ["OPENAI_API_KEY"]), settings.model)
outcomes = [draft_reply(ticket_id, records, provider, settings).summary() for ticket_id in sorted(records.tickets)]
for outcome in outcomes:
    print(json.dumps(outcome, ensure_ascii=False))
results = Path("results")
results.mkdir(exist_ok=True)
path = results / f"live-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
path.write_text(json.dumps({"requested_model": settings.model, "outcomes": outcomes}, indent=2, ensure_ascii=False),
                encoding="utf-8")
print(f"Wrote {path}. Review every draft yourself: a 'ready' status means it passed checks, not that it is good.")
