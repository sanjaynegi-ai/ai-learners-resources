"""Compare prompt versions on a fixed evaluation set, with explicit denominators.

    refund-drafts-compare                                   # offline REPLAY of synthetic recordings (method only)
    refund-drafts-compare --live --confirm-paid-calls       # real provider; costs money; results are model evidence

The replay provider returns hand-written outputs from fixtures/replay/. It proves the harness, metrics and
decision process work. It says NOTHING about which prompt a real model would do better with.
"""
import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from .config import ConfigError, Settings, settings_from_env
from .domain import FIXTURES, load_records
from .pipeline import Outcome, draft_reply
from .prompt import ModelRequest
from .providers import OpenAIProvider, ProviderResult, make_openai_client
from .validate import DEFAULT_CHECKS, Check

VERSIONS = ("refund_reply_v1", "refund_reply_v2")


@dataclass
class ReplayProvider:
    """Returns recorded text keyed by (prompt version, ticket). Synthetic: a test double, not a model."""
    recordings: dict[str, dict[str, dict]]
    name: str = "replay"

    def generate(self, request: ModelRequest, *, timeout_s: float, max_output_tokens: int) -> ProviderResult:
        recording = self.recordings[request.prompt_version][request.ticket_id]
        return ProviderResult("completed", recording["text"], None, None, None, "synthetic-replay")


def load_recordings(directory: Path = FIXTURES / "replay") -> dict[str, dict[str, dict]]:
    return {version: json.loads((directory / f"{version}.json").read_text(encoding="utf-8")) for version in VERSIONS}


def evaluate(provider, settings: Settings, checks: tuple[Check, ...] = DEFAULT_CHECKS,
             versions: tuple[str, ...] = VERSIONS) -> dict[str, dict]:
    records = load_records(FIXTURES / "eval")
    expected = {key: value for key, value in json.loads((FIXTURES / "eval" / "expectations.json").read_text(encoding="utf-8")).items()
                if not key.startswith("_")}
    report = {}
    for version in versions:
        outcomes: dict[str, Outcome] = {ticket_id: draft_reply(ticket_id, records, provider, settings, checks=checks,
                                                               prompt_version=version, sleep=lambda _: None)
                                        for ticket_id in sorted(expected)}
        should_answer = [t for t in expected if expected[t] == "ready"]
        should_escalate = [t for t in expected if expected[t] == "needs_agent"]
        report[version] = {
            "matches_expected": (sum(outcomes[t].status == expected[t] for t in expected), len(expected)),
            "unsafe_ready": (sorted(t for t in should_escalate if outcomes[t].status == "ready"), len(should_escalate)),
            "unnecessary_escalation": (sorted(t for t in should_answer if outcomes[t].status == "needs_agent"), len(should_answer)),
            "failed": (sorted(t for t in expected if outcomes[t].status == "failed"), len(expected)),
            "outcomes": {t: {"status": o.status, "reasons": o.reasons, "attempts": o.attempts} for t, o in outcomes.items()},
        }
    return report


def print_report(report: dict, provider_name: str, recordings: dict | None) -> None:
    if provider_name == "replay":
        print("REPLAY OF SYNTHETIC RECORDINGS: demonstrates the comparison method, not model quality.\n")
    for version, result in report.items():
        matched, total = result["matches_expected"]
        print(f"{version}: outcome matches expectation {matched}/{total}")
        for key, label in (("unsafe_ready", "UNSAFE ready (should have gone to an agent)"),
                           ("unnecessary_escalation", "unnecessary escalation (could have answered)"),
                           ("failed", "failed (no usable output)")):
            tickets, denominator = result[key]
            print(f"  {label}: {len(tickets)}/{denominator} {tickets if tickets else ''}")
        if recordings:
            notes = {t: r["reviewer_note"] for t, r in recordings[version].items()
                     if isinstance(r, dict) and "reviewer_note" in r and result["outcomes"][t]["status"] == "ready"}
            for ticket_id, note in sorted(notes.items()):
                print(f"  human review on a ready draft, {ticket_id}: {note}")
        print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compare prompt versions on the fixed evaluation set")
    parser.add_argument("--live", action="store_true", help="Use the real provider (paid)")
    parser.add_argument("--confirm-paid-calls", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON")
    args = parser.parse_args(argv)
    if args.live:
        if not args.confirm_paid_calls:
            sys.exit("Refusing to run: --live makes paid API calls. Add --confirm-paid-calls if you intend that.")
        try:
            settings = settings_from_env()
        except ConfigError as error:
            sys.exit(f"Configuration error: {error}")
        if settings.provider != "openai":
            sys.exit("Set REFUND_DRAFTS_PROVIDER=openai for --live.")
        provider, recordings = OpenAIProvider(make_openai_client(os.environ["OPENAI_API_KEY"]), settings.model), None
    else:
        settings, recordings = Settings(), load_recordings()
        provider = ReplayProvider(recordings)
    report = evaluate(provider, settings)
    print(json.dumps(report, indent=2, ensure_ascii=False)) if args.json else print_report(report, provider.name, recordings)


if __name__ == "__main__":
    main()
