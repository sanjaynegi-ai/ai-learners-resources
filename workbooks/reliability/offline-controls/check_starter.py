"""Run explicitly after completing approval_starter.py; not a default passing reference test."""
from approval_starter import authorize

assert authorize(50, ['sam'], {'sam', 'lee'}) is True
assert authorize(60, ['sam', 'lee'], {'sam', 'lee'}) is True
for approvers, current in ((['sam', 'sam'], {'sam', 'lee'}), (['sam', 'lee'], {'sam'})):
    try:
        authorize(60, approvers, current)
    except PermissionError:
        pass
    else:
        raise AssertionError('Missing/revoked distinct approval was accepted')
print('Starter behavioral checks passed; explain your implementation independently.')
