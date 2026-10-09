import difflib,json,shutil
from pathlib import Path
from ecology.services import judge
root=Path('studies/tool_ecology/runs/demand-engineering-01/seed-9001/local-boids')
slot=root/'builders/a00/round-01'
out=root/'diagnostics-helper-scope-02'
if out.exists():raise ValueError('preserve earlier diagnostic')
shutil.copytree(slot/'judge-view',out/'view')
p=out/'view/published/a00_r01/__init__.py'
old=p.read_text();new=old.replace('def _base(rows, request):','def _base(rows, request, normalize=True):')
region="out['region'] = row.get('region').strip().lower() if isinstance(row.get('region'), str) else row.get('region')"
new=new.replace(region,"out['region'] = ("+region.split(" = ",1)[1]+") if normalize else row.get('region')",1)
new=new.replace('return _base(rows, request)','return _base(rows, request, normalize=False)',1)
start=new.index('def window(');new=new[:start]+new[start:].replace('data = _base(rows, request)','data = _base(rows, request, normalize=False)',1)
p.write_text(new)
meta=json.loads((root/'registry/a00_r01.json').read_text())
image=json.loads(Path('studies/tool_ecology/runs/demand-engineering-01/manifest.json').read_text())['image']
result=judge(out/'view',meta,out/'grade',image,seed=9001,round_=1,instrument=False)
original=json.loads((slot/'service/result.json').read_text())
dest=Path('studies/tool_ecology/evidence/v03/engineering-01')
(dest/'helper-scope.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/a00_r01/__init__.py',tofile='diagnostic-only/a00_r01/__init__.py')))
report=dict(classification='posthoc_host_authored_diagnostic_not_original_score',original=original['families'],diagnostic=result['families'],explanation='Common helper normalizes region, but revenue/window must preserve original region; scope normalization to only the four families that require it.',model_calls=0)
(dest/'helper-scope-diagnosis.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert all(x['passed']==x['total'] for x in result['families'].values())
