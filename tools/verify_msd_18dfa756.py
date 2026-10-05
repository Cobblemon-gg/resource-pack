#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,re,zipfile
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'reports/mega-showdown-18dfa756'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=json.loads((OUT/'port.json').read_text());before=r['before_asset_hashes'];after={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'assets').rglob('*') if p.is_file()};updates={x['target'] for x in r['updates']}
 assert set(before)==set(after),'Assets unexpectedly added/deleted'
 assert {p for p in before if before[p]!=after[p]}==updates
 assert sha(ROOT/'client-baseline.json')==r['baseline_sha256']
 assert sha(ROOT.parent/'atlas/client/resource-pack/atlas-baseline.zip')==r['client_archive_sha256']
 locators=0
 for row in r['updates']:
  p=row['target'];assert sha(ROOT/p)==row['after_sha256'];a=json.loads((OUT/'before'/p).read_text());b=json.loads((ROOT/p).read_text());ag=a['minecraft:geometry'][0];bg=b['minecraft:geometry'][0]
  aa={x['name']:x for x in ag['bones']};bb={x['name']:x for x in bg['bones']};assert len(bb)==len(bg['bones'])
  assert set(aa)<=set(bb)
  for name,bone in bb.items():
   assert not bone.get('parent') or bone['parent'] in bb
   if name not in aa:assert bone.get('locators') and not bone.get('cubes')
   else:
    assert bone.get('cubes')==aa[name].get('cubes'),(p,name,'changed cubes')
    if name not in row['changed_bones']:assert bone==aa[name]
    elif bone.get('cubes'):assert {k:v for k,v in bone.items() if k!='locators'}=={k:v for k,v in aa[name].items() if k!='locators'}
   locators+=len(bone.get('locators',{}))
  assert not any(x in p for x in ['crowned','primal'])
  bd=dict(bg['description']);ad=dict(ag['description'])
  for k in row['bounds']:bd.pop(k,None);ad.pop(k,None)
  assert ad==bd
 # Existing resolver states stay exact, so established audit states remain applicable.
 oldrows=json.loads((OUT/'new-overlay.json').read_text())['checks']
 ids={Path(p).name[:-5] for p in updates}
 rows=[x for x in oldrows if x['declared'] and x['assets'].get('model','').split(':')[-1] in ids and not any('crowned' in a or 'primal' in a for a in x['aspects'])]
 commands=[]
 for x in rows:
  a=x['aspects'];commands.append(' '.join(['/spawnpokemon',x['species'].split(':')[-1],'shiny='+str('shiny' in a).lower()]+[('gender=' if v in ['male','female','genderless'] else 'aspect=')+v for v in a if v!='shiny']))
 commands=sorted(set(commands));(OUT/'spawn-commands.txt').write_text('\n'.join(commands)+'\n')
 (OUT/'affected-states.json').write_text(json.dumps(rows,indent=2)+'\n')
 result={'status':'passed','updated_assets':len(updates),'upstream_models_ported':len({x['source'] for x in r['updates']}),'spawn_commands':len(commands),'species':len({x['species'] for x in rows}),'cubes_uv_textures_resolvers_unchanged':True,'baseline_unchanged':True,'deletions':0}
 previous=json.loads((OUT/'before-overlay.json').read_text())['checks']
 key=lambda x:(x['species'],tuple(x['aspects']))
 previous={key(x):x for x in previous};current={key(x):x for x in oldrows}
 normalize=lambda x:sorted(json.dumps({k:v for k,v in i.items() if k!='source'},sort_keys=True) for i in x['issues'])
 assert previous.keys()==current.keys()
 assert all(normalize(previous[k])==normalize(current[k]) and previous[k]['assets']==current[k]['assets'] for k in previous)
 result.update(renderer_states_checked=len(previous),new_renderer_findings=0,renderer_issues_identical_before_after=True)
 (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
