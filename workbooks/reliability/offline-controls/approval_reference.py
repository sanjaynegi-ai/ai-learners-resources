"""Reference policy and least-privilege dispatcher; all approvals are trusted fixtures."""


def authorize(amount, approvers, current_operators):
    if type(amount) is not int or not 0 < amount <= 100:
        raise ValueError('Amount outside synthetic policy')
    if not isinstance(approvers, (list, tuple)) or any(not isinstance(a, str) for a in approvers):
        raise ValueError('Invalid approval record')
    distinct = set(approvers)
    required = 2 if amount > 50 else 1
    if not distinct <= set(current_operators) or len(distinct) < required:
        raise PermissionError('Current distinct approvals required')
    return True


def dispatch_refund(store, identity, arguments, trusted_approvers, current_operators):
    if not isinstance(arguments, dict) or set(arguments) != {'key', 'amount'}:
        raise PermissionError('Tool arguments cannot supply identity, role or approval')
    authorize(arguments['amount'], trusted_approvers, current_operators)
    return store.refund(identity, arguments['key'], arguments['amount'], approved=True)
