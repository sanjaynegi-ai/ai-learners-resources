"""Draft replies for fixture tickets.

    refund-drafts --ticket T-001                 # offline fake provider (default)
    refund-drafts --all                          # every fixture ticket, with outcome counts
    refund-drafts --ticket T-001 --fault timeout --fault timeout    # scripted provider faults (fake only)

The live OpenAI route needs REFUND_DRAFTS_PROVIDER=openai, OPENAI_API_KEY and OPENAI_MODEL, and costs money.
"""
import argparse
import json
import os
from collections import Counter

from .config import ConfigError, settings_from_env
from .domain import load_records
from .pipeline import draft_reply
from .providers import FAULTS, FakeProvider, OpenAIProvider, make_openai_client


def build_provider(settings, faults):
    if settings.provider == "openai":
        if faults:
            raise ConfigError("--fault only applies to the offline fake provider")
        return OpenAIProvider(make_openai_client(os.environ["OPENAI_API_KEY"]), settings.model)
    return FakeProvider(script=list(faults))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="QuickCart refund reply drafts (synthetic fixtures)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ticket")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--fault", action="append", default=[], choices=FAULTS,
                        help="Fake provider only: script the next call's behavior; repeat for later calls")
    args = parser.parse_args(argv)
    try:
        settings = settings_from_env()
        provider = build_provider(settings, args.fault)
    except ConfigError as error:
        raise SystemExit(f"Configuration error: {error}")
    records = load_records()
    ticket_ids = sorted(records.tickets) if args.all else [args.ticket]
    outcomes = [draft_reply(ticket_id, records, provider, settings) for ticket_id in ticket_ids]
    for outcome in outcomes:
        print(json.dumps(outcome.summary(), ensure_ascii=False))
    if args.all:
        counts = Counter(outcome.status for outcome in outcomes)
        total = len(outcomes)
        print(json.dumps({"provider": provider.name, "tickets": total,
                          **{status: f"{counts[status]}/{total}" for status in ("ready", "needs_agent", "failed")},
                          "provider_calls": sum(outcome.attempts for outcome in outcomes)}))


if __name__ == "__main__":
    main()
