"""Independent exercise: a contamination gate for release decisions.

A prompt (instructions, few-shot examples) must not contain evaluation cases. If it does, the held-out score
measures memory of those cases, not the behavior you will get on new tickets.

Implement:
  find_contaminated(prompt_text, cases, min_words=6) -> sorted list of case_ids whose ticket text
      * appears verbatim in prompt_text (compare after normalizing case and whitespace), OR
      * shares a run of at least `min_words` consecutive words with prompt_text, after lowercasing and
        removing punctuation (catches lightly edited copies of longer tickets).
  contamination_gate(baseline, candidate) -> ("fail", detail) if any held-out case is found in the candidate's
      prompt, else ("pass", detail). Use refund_drafts.prompt.load_instructions(candidate.manifest["prompt_version"])
      and the held-out cases from eval_harness.dataset.load().

Do not open contamination_reference.py until you have recorded your own attempt.
"""


def find_contaminated(prompt_text: str, cases: list[dict], min_words: int = 6) -> list[str]:
    # TODO 1: normalize text (lowercase, collapse whitespace; for n-grams also strip punctuation).
    # TODO 2: flag exact (normalized) substring matches.
    # TODO 3: flag shared runs of >= min_words consecutive words.
    raise NotImplementedError("Implement find_contaminated")


def contamination_gate(baseline, candidate) -> tuple[str, str]:
    # TODO 4: load the candidate prompt and held-out cases; return ("fail", ...) or ("pass", ...).
    raise NotImplementedError("Implement contamination_gate")
