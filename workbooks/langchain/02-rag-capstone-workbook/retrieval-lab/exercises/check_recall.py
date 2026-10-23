import argparse
import importlib.util
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--reference', action='store_true')
args = parser.parse_args()
path = Path(__file__).with_name('recall_policy_reference.py' if args.reference else 'recall_policy.py')
spec = importlib.util.spec_from_file_location('policy', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for published, withdrawn, now, expected in ((100, None, 99, False), (100, None, 100, True),
                                           (100, 200, 199, True), (100, 200, 200, False),
                                           (100, 100, 100, False)):
    assert module.eligible(published_at=published, withdrawn_at=withdrawn, now=now) is expected
for published, withdrawn, now in ((True, None, 100), (-1, None, 100), (100, 99, 100)):
    try:
        module.eligible(published_at=published, withdrawn_at=withdrawn, now=now)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid input accepted')
print('Recall policy acceptance checks passed; integration and ownership evidence still required.')
