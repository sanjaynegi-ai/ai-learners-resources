"""Run explicitly after completing priority.py; not part of the default passing test suite.

Usage from the python-bridge directory:
    uv run python exercises/check_priority.py              # checks your priority.py
    uv run python exercises/check_priority.py --reference  # checks the inspectable reference
"""
import importlib
import sys
from quickcart_bridge.models import Ticket

module = importlib.import_module('priority_reference' if '--reference' in sys.argv else 'priority')
priority_ids = module.priority_ids

tickets = [Ticket('QC-B', 20), Ticket('QC-A', 20), Ticket('QC-C', 5, ('shipping', 'shipping')), Ticket('QC-D', 50)]
original = list(tickets)
assert priority_ids(tickets, 20) == ['QC-D', 'QC-A', 'QC-B'], 'Descending amount, ID tie-break, inclusive threshold'
assert tickets == original, 'Input list must not be reordered or mutated'
assert priority_ids(tickets, 0) == ['QC-D', 'QC-A', 'QC-B', 'QC-C'], 'Duplicate tags are still one ticket'
assert priority_ids(tickets, 51) == [] and priority_ids([], 0) == []
for threshold in (True, -1, 2.5, '20', None):
    try:
        priority_ids(tickets, threshold)
    except ValueError:
        pass
    else:
        raise AssertionError(f'Invalid threshold accepted: {threshold!r}')
print(f'{module.__name__}: priority behavioral checks passed; explain your implementation independently.')
