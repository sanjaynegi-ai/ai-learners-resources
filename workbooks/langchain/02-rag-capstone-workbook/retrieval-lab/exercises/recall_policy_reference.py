"""Public reasoning aid, not proof of independent completion."""
def eligible(*, published_at, withdrawn_at, now):
    values = [published_at, now] + ([] if withdrawn_at is None else [withdrawn_at])
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("Nonnegative integer timestamps required")
    if withdrawn_at is not None and withdrawn_at < published_at:
        raise ValueError("Withdrawal precedes publication")
    return published_at <= now and (withdrawn_at is None or now < withdrawn_at)
