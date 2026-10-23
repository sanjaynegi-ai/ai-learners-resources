"""Run an actual local provider-failure incident; keep rollout halted after recovery."""
import argparse
import asyncio
import json
from pathlib import Path

from .core import Engine, OfflineProvider, fixture_paths


async def drill(out):
    out.mkdir(parents=True, exist_ok=False)
    engine = Engine(out/"state", *fixture_paths())
    timeline = []
    try:
        baseline = await engine.ask("demo-agent-a", "refund")
        class Outage(OfflineProvider):
            async def generate(self, evidence):
                raise RuntimeError("synthetic provider outage; raw payload must not be logged")
        engine.provider = Outage()
        failure = await engine.ask("demo-agent-a", "refund")
        timeline.append({"step": 1, "action": "observed failed outcome after provider boundary change"})
        engine.halt()
        timeline.append({"step": 2, "action": "application-oncall halted model admissions and simulated actions"})
        engine.provider = OfflineProvider()
        held = await engine.ask("demo-agent-a", "refund")
        # Probe recovery on a separate state copy; production halt remains intact.
        probe = Engine(out/"probe", *fixture_paths())
        try:
            recovered = await probe.ask("demo-agent-a", "refund")
        finally:
            probe.close()
        timeline.append({"step": 3, "action": "restore known offline provider; fresh isolated recovery probe passes"})
        assert baseline["status"] == recovered["status"] == "ready"
        assert failure["status"] == "failed" and held["status"] == "budget_or_halt"
        summary = {"kind": "synthetic", "time_basis": "ordered steps, not response-time claims",
                   "baseline": baseline["status"], "failure": failure["status"], "held": held["status"],
                   "recovery": recovered["status"], "rollout_halted": True, "timeline": timeline,
                   "diagnosis": "provider boundary fails; unchanged retrieval/policy succeeds with restored provider",
                   "owner": "application-oncall", "resume": "pending separate review"}
        (out/"incident.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
        (out/"runbook-update.md").write_text("# Exercise amendment\n\nApplication-oncall must distinguish provider failure from missing evidence. Halt admissions and actions; restore a compatible provider/configuration; probe separately without lifting the active halt. Reviewer checks fresh semantic and control evidence before resume.\n", encoding="utf-8")
        return summary
    finally:
        engine.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    print(json.dumps(asyncio.run(drill(p.parse_args().out)), indent=2))
