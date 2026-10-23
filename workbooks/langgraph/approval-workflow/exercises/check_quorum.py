import argparse,importlib.util
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--reference',action='store_true');a=p.parse_args()
path=Path(__file__).with_name('quorum_reference.py' if a.reference else 'quorum.py')
spec=importlib.util.spec_from_file_location('quorum',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
one={'id':'S1','tenant':'A','role':'supervisor','active':True}
two={**one,'id':'S2'}
assert m.quorum('agent','A',[one,two]) is True
assert m.quorum('agent','A',[one,one]) is False
assert m.quorum('S1','A',[one,two]) is False
assert m.quorum('agent','A',[one,{**two,'active':False}]) is False
assert m.quorum('agent','A',[one,{**two,'tenant':'B'}]) is False
assert m.quorum('agent','A',[one,{**two,'role':'agent'}]) is False
print('Quorum checks pass; durable schema, revocation and recovery integration remain learner evidence.')
