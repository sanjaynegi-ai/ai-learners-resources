"""Independent change-feed adapter. No reference imports in your implementation."""


def apply_events(store, events):
    """Validate the WHOLE batch before writes, then process in order.

    Upsert: exactly {operation, source, raw, metadata}; delete: exactly
    {operation, source}. Unknown operation/keys or malformed basic field
    types must raise ValueError without changing any source. At most 20
    events. Source is a flat lowercase ID matching the publisher contract;
    metadata has exactly tenant/roles/expires/topic/claim/value and their
    publisher types. This validates shape, not extractability or meaning.

    Once shape is valid, return one report per event in order. Publish via
    store.publish and retain quarantined reports; never retry them silently.
    Delete explicitly via store.delete, returning {status: deleted}.
    Omission from an incremental feed must NEVER delete another source.
    Content failures are source-level quarantine, not atomic-batch rollback.
    """
    raise NotImplementedError("Build the bounded incremental change-feed adapter")
