import argparse
import importlib.util
from pathlib import Path
from langchain_core.documents import Document
from lc_mechanisms.demo import QUOTE, retriever, composed

parser = argparse.ArgumentParser()
parser.add_argument('--reference', action='store_true')
args = parser.parse_args()
name = 'context_budget_reference.py' if args.reference else 'context_budget.py'
spec = importlib.util.spec_from_file_location('selection', Path(__file__).with_name(name))
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
one = Document(page_content='alpha', metadata={'source':'A','revision':1})
two = Document(page_content='beta', metadata={'source':'B','revision':1})
docs = [one, one.model_copy(deep=True), two]
before = [d.model_dump() for d in docs]
assert module.select_documents(docs, 9) == [one,two]
assert module.select_documents(docs, 5) == [one]
assert module.select_documents(docs, 4) == [two]  # Skip a large passage; do not truncate it.
assert before == [d.model_dump() for d in docs]
for budget in (True,0,-1):
    try: module.select_documents(docs,budget)
    except ValueError: pass
    else: raise AssertionError('Invalid budget accepted')
conflict = Document(page_content='different', metadata={'source':'A','revision':1})
try: module.select_documents([one,conflict],20)
except ValueError: pass
else: raise AssertionError('Conflicting source identity accepted')
selected = module.select_documents(retriever().invoke('DELAY-42'), len(QUOTE))
assert composed().invoke({'evidence': '\n'.join(d.page_content for d in selected), 'question':'code?'}).quote == QUOTE
skipped = module.select_documents(retriever().invoke('DELAY-42'), 1)
try: composed().invoke({'evidence':'\n'.join(d.page_content for d in skipped), 'question':'code?'})
except ValueError: pass
else: raise AssertionError('Skipped evidence was credited as a supported answer')
print('Context budget checks passed; integrate into your retriever and defend the skipped evidence.')
