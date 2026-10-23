"""Command line for the evaluation harness. Every run is SIMULATED and recorded in results/registry.jsonl.

    eval-harness run --prompt refund_reply_v2 --split dev [--cases]
    eval-harness decide --baseline refund_reply_v1 --candidate refund_reply_v2
"""
import argparse
import json

from .decide import decide, record
from .harness import run

BANNER = "SIMULATED MODEL: these results teach the evaluation method; they are not evidence about any real model."


def show_run(result, with_cases: bool) -> None:
    m, s = result.manifest, result.summary
    print(f"{m['prompt_version']} on {m['split']} ({s['cases']} cases) | dataset {m['dataset_version']} {m['dataset_sha256']} | "
          f"prompt {m['prompt_sha256']} | harness {m['harness_sha256']}")
    for key in ("correct", "coverage", "harmful_ready", "unnecessary_escalation", "wrong_language_ready", "failed"):
        rate = s[key]
        print(f"  {key:24} {rate['k']}/{rate['n']}  ci95 {rate['ci95']}")
    print(f"  latency p50/p95          {s['latency_s']['p50']} / {s['latency_s']['p95']} s (simulated)")
    print(f"  cost per 1,000 requests  ${s['cost_usd_per_1000']} (hypothetical prices); calls per case {s['provider_calls_per_case']}")
    print("  slices: " + "; ".join(f"{name} {v['correct']['k']}/{v['correct']['n']} harmful {v['harmful']}"
                                   for name, v in result.slices.items()))
    if with_cases:
        for row in result.rows:
            if not row["correct"]:
                print(f"    {row['case_id']} {row['language']} {row['category']:13} expect {row['expect']:11} got "
                      f"{row['status']:11} {', '.join(row['problems']) or ('wrong_language' if row['wrong_language'] else '')}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Versioned evaluation of the refund-draft pipeline (simulated model)")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--prompt", required=True)
    run_parser.add_argument("--split", choices=["dev", "heldout"], default="dev")
    run_parser.add_argument("--cases", action="store_true", help="List every incorrect case")
    decide_parser = commands.add_parser("decide")
    decide_parser.add_argument("--baseline", required=True)
    decide_parser.add_argument("--candidate", required=True)
    decide_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    print(BANNER)
    if args.command == "run":
        if args.split == "heldout":
            print("Held-out runs are recorded; each new candidate scored here uses up some of its independence.")
        result = run(args.prompt, args.split)
        record(result)
        show_run(result, args.cases)
        return
    baseline, candidate = run(args.baseline, "heldout"), run(args.candidate, "heldout")
    for result in (baseline, candidate):
        record(result)
    report = decide(baseline, candidate)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return
    for result in (baseline, candidate):
        show_run(result, False)
    print(f"\nGates {report['gates_version']} (sha256 {report['gates_sha256']}): "
          f"{report['candidate']} vs {report['baseline']} on held-out")
    for gate in report["gates"]:
        mark = {"pass": "PASS", "fail": "FAIL", "insufficient": "N/A "}[gate["status"]]
        print(f"  [{mark}] {'(critical) ' if gate['critical'] else ''}{gate['gate']}: {gate['detail']}")
    for warning in report["warnings"]:
        print(f"  WARNING: {warning}")
    print(f"\nDecision: {report['decision']}" + (f" (failed: {', '.join(report['failed_gates'])})" if report["failed_gates"] else ""))


if __name__ == "__main__":
    main()
