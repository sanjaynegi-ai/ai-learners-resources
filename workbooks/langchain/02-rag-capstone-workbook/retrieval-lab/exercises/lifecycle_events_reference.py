"""Inspect only after an independent attempt."""
import re


def apply_events(store, events):
    if not isinstance(events, list) or len(events) > 20:
        raise ValueError("Require list of at most 20 events")
    fields = {"tenant", "roles", "expires", "topic", "claim", "value"}
    for event in events:
        if not isinstance(event, dict) or event.get("operation") not in ("upsert", "delete"):
            raise ValueError("Invalid event")
        expected = {"operation", "source"} | ({"raw", "metadata"} if event["operation"] == "upsert" else set())
        source = event.get("source")
        if set(event) != expected or not isinstance(source, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,79}", source):
            raise ValueError("Invalid event shape/source")
        if event["operation"] == "upsert":
            m = event["metadata"]
            if (not isinstance(event["raw"], str) or not isinstance(m, dict) or set(m) != fields
                    or type(m["expires"]) is not int or not isinstance(m["roles"], list) or not m["roles"]
                    or any(not isinstance(role, str) or not role for role in m["roles"])
                    or any(not isinstance(m[k], str) or not m[k] for k in fields - {"roles", "expires"})):
                raise ValueError("Invalid upsert contract")
    reports = []
    for event in events:
        if event["operation"] == "delete":
            store.delete(event["source"])
            reports.append({"status": "deleted"})
        else:
            reports.append(store.publish(event["source"], event["raw"], event["metadata"]))
    return reports
