"""Inspect metric denominators on authored cases, not real-model quality."""
import hashlib
import json
from pathlib import Path
import time
from controls import validate_answer

ROOT = Path(__file__).resolve().parent


def evaluate():
    data = json.loads((ROOT/'evaluation-fixtures.json').read_text(encoding='utf-8'))
    records = []
    for case in data['cases']:
        start = time.perf_counter()
        row = {'id': case['id'], 'answered':False, 'supported':False, 'appropriate_abstention':False,
               'failed':False, 'attempt_units':case['attempt_units'], 'review_minutes':case['review_minutes']}
        try:
            if 'error' in case:
                raise TimeoutError(case['error'])
            result = validate_answer(case['result'], ['A'])
            row['answered'] = result['status']=='answered'
            row['supported'] = row['answered'] and result['answer']==case['expected']
            row['appropriate_abstention'] = result['status']=='abstained' and case['expected'] is None
        except (ValueError, TimeoutError) as error:
            row['failed'] = True
            row['failure_class'] = type(error).__name__
        row['local_validation_ms'] = (time.perf_counter()-start)*1000
        records.append(row)
    requests = len(records)
    answered = sum(r['answered'] for r in records)
    supported = sum(r['supported'] for r in records)
    abstained = sum(r['appropriate_abstention'] for r in records)
    useful = supported+abstained
    cost = sum(r['attempt_units'] for r in records)
    files = ('controls.py','approval_reference.py','evaluate_fixture.py','evaluation-fixtures.json','uv.lock')
    return {'application_version':'quickcart-offline-controls-0.2.0',
            'hashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
            'prompt_version':'none; no model prompt executed', 'model':'none; authored fixture results',
            'configuration':{'evaluation':'local contract validation only','schema':'answer-contract-v1'},
            'dataset_version':data['version'],'label_policy':data['label_policy'], 'requests':requests,
            'coverage':{'numerator':answered,'denominator':requests},
            'supported_answer_rate':{'numerator':supported,'denominator':answered or None},
            'useful_outcome_rate':{'numerator':useful,'denominator':requests},
            'appropriate_abstentions':abstained,'failures':sum(r['failed'] for r in records),
            'unsupported_answers':answered-supported,
            'local_validation_latency_ms':{'sum':sum(r['local_validation_ms'] for r in records),
                'denominator':requests, 'mean':sum(r['local_validation_ms'] for r in records)/requests if requests else None},
            'synthetic_attempt_units':cost,'units_per_request':cost/requests if requests else None,
            'units_per_useful_outcome':cost/useful if useful else None,
            'hypothetical_review_minutes':sum(r['review_minutes'] for r in records),
            'hypothetical_review_minutes_per_request':sum(r['review_minutes'] for r in records)/requests if requests else None,
            'records':records, 'limits':'Authored four-case development illustration; no held-out generalization, real provider cost or model quality claim.'}


if __name__=='__main__':
    print(json.dumps(evaluate(),indent=2))
