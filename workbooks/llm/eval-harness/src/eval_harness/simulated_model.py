"""A SIMULATED model for evaluation practice. Not a real model, and not evidence about any real model.

Each prompt version has a behavior profile: how often it claims a pending refund was issued, answers
out-of-scope requests, follows injected instructions, replies in the wrong language, escalates answerable
tickets, or returns malformed output. Randomness is seeded by (profile family, case, attempt), so every run is
reproducible. Prompt versions in the same family share seeds, so they fail on the same cases unless something
else changes. A real evaluation replaces this with live calls (W-LLM-API-01's provider boundary).
"""
import json
import random
from dataclasses import dataclass, field

from refund_drafts.prompt import ModelRequest
from refund_drafts.providers import ProviderResult

CORRECT = {
    "en": "Thank you for your patience. Your refund was issued and should reach you by {date}.",
    "de": "Vielen Dank für Ihre Geduld. Ihre Rückerstattung wurde veranlasst und sollte bis {date} bei Ihnen sein.",
    "hi": "धन्यवाद। आपका रिफंड जारी कर दिया गया है और {date} तक आपके पास पहुँच जाना चाहिए।",
}
HOLDING = {
    "en": "Thank you for your message. An agent will check your request and reply shortly.",
    "de": "Vielen Dank für Ihre Nachricht. Ein Mitarbeiter prüft Ihr Anliegen und antwortet in Kürze.",
    "hi": "आपके संदेश के लिए धन्यवाद। एक एजेंट आपके अनुरोध की जाँच करके जल्द जवाब देगा।",
}
CLAIM_ISSUED = "Good news: your refund has been issued and is on its way."
OUT_OF_SCOPE_ANSWER = "No problem, we will arrange that for you. Your refund should reach you by {date}."
OBEY_INJECTION = "As requested, your refund of {amount} will arrive today."


@dataclass(frozen=True)
class Profile:
    family: str
    claim_issued: float
    answer_out_of_scope: float
    obey_injection: float
    wrong_language: dict
    over_abstain: float
    malformed: float
    output_tokens: int
    latency: tuple[float, float]


PROFILES = {
    "refund_reply_v1": Profile("v1", 0.5, 0.6, 0.4, {"de": 0.5, "hi": 0.7}, 0.05, 0.03, 110, (1.5, 3.5)),
    "refund_reply_v2": Profile("v2", 0.12, 0.2, 0.1, {"de": 0.1, "hi": 0.3}, 0.15, 0.06, 130, (1.8, 4.0)),
    # v3 is v2 plus few-shot examples; same behavior family, longer prompt, slightly longer answers.
    "refund_reply_v3": Profile("v2", 0.12, 0.2, 0.1, {"de": 0.1, "hi": 0.3}, 0.15, 0.06, 140, (1.8, 4.0)),
}


@dataclass
class SimulatedModel:
    cases: dict[str, dict]                       # case_id -> case (the simulator may read the answer key)
    name: str = "simulated"
    latency_s: dict[str, float] = field(default_factory=dict)
    _attempts: dict[str, int] = field(default_factory=dict)

    def generate(self, request: ModelRequest, *, timeout_s: float, max_output_tokens: int) -> ProviderResult:
        profile = PROFILES[request.prompt_version]
        case = self.cases[request.ticket_id]
        attempt = self._attempts.get(case["case_id"], 0) + 1
        self._attempts[case["case_id"]] = attempt
        rng = random.Random(f"{profile.family}|{case['case_id']}|{attempt}")
        self.latency_s[case["case_id"]] = self.latency_s.get(case["case_id"], 0.0) + rng.uniform(*profile.latency)
        tokens_in = (len(request.instructions) + len(request.input_text)) // 4
        tokens_out = int(profile.output_tokens * rng.uniform(0.9, 1.1))
        model = f"simulated:{profile.family}"
        if rng.random() < profile.malformed:
            return ProviderResult("completed", "```json\n" + self._json(self._intended(case, rng, profile)) + "\n```",
                                  None, tokens_in, tokens_out, model)
        # A model shown this exact ticket in its examples reproduces the example's correct answer.
        behavior = self._correct(case) if case["ticket_text"] in request.instructions else self._intended(case, rng, profile)
        return ProviderResult("completed", self._json(behavior), None, tokens_in, tokens_out, model)

    @staticmethod
    def _json(payload: dict) -> str:
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _correct(case: dict) -> dict:
        order, language = case["order"], case["language"]
        if case["expect"] == "ready":
            date = order["expected_refund_date"]
            return {"reply_text": CORRECT[language].format(date=date), "refund_date_used": date, "needs_agent": False}
        return {"reply_text": HOLDING[language], "refund_date_used": None, "needs_agent": True}

    def _intended(self, case: dict, rng: random.Random, profile: Profile) -> dict:
        order, language, category = case["order"], case["language"], case["category"]
        date = order["expected_refund_date"]
        if category in ("pending", "not_requested"):
            if rng.random() < profile.claim_issued:
                return {"reply_text": CLAIM_ISSUED, "refund_date_used": None, "needs_agent": False}
        elif category == "out_of_scope":
            if rng.random() < profile.answer_out_of_scope:
                return {"reply_text": OUT_OF_SCOPE_ANSWER.format(date=date), "refund_date_used": date, "needs_agent": False}
        elif category == "injection":
            if rng.random() < profile.obey_injection:
                amount = next((w for w in case["ticket_text"].split() if w.count(".") == 1 and w.replace(".", "").isdigit()), "500.00")
                return {"reply_text": OBEY_INJECTION.format(amount=amount), "refund_date_used": None, "needs_agent": False}
        if case["expect"] == "ready":
            if rng.random() < profile.over_abstain:
                return {"reply_text": HOLDING[language], "refund_date_used": None, "needs_agent": True}
            if rng.random() < profile.wrong_language.get(language, 0.0):
                return {"reply_text": CORRECT["en"].format(date=date), "refund_date_used": date, "needs_agent": False}
        return self._correct(case)
