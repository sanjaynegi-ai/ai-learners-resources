"""Inspectable reference for the contamination gate. Consulting it is disclosed assistance, not independent evidence."""
import re

from refund_drafts.prompt import load_instructions

from eval_harness import dataset


def _normal(text: str) -> str:
    return " ".join(text.lower().split())


def _words(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _ngrams(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def find_contaminated(prompt_text: str, cases: list[dict], min_words: int = 6) -> list[str]:
    prompt_normal = _normal(prompt_text)
    prompt_grams = _ngrams(_words(prompt_text), min_words)
    found = []
    for case in cases:
        text = case["ticket_text"]
        if _normal(text) in prompt_normal or _ngrams(_words(text), min_words) & prompt_grams:
            found.append(case["case_id"])
    return sorted(found)


def contamination_gate(baseline, candidate) -> tuple[str, str]:
    heldout = [c for c in dataset.load()["cases"] if c["split"] == "heldout"]
    found = find_contaminated(load_instructions(candidate.manifest["prompt_version"]), heldout)
    if found:
        return "fail", f"{len(found)}/{len(heldout)} held-out cases appear in the prompt: {', '.join(found)}"
    return "pass", f"0/{len(heldout)} held-out cases found in the prompt"
