from pathlib import Path
import json,zipfile,hashlib
R=Path('/Users/daniel/IdeaProjects/Cobblemon/resource-pack');O=Path(__file__).parent;m=json.loads((O/'manifest.json').read_text());D=R/'reports/shadow-20260910/config-additions'
def select(d,cmd,pulling=0,pull=0):
 result=None;state={'custom_model_data':cmd,'pulling':pulling,'pull':pull}
 for v in d.get('overrides',[]):
  if all(state.get(k,0)>=threshold for k,threshold in v['predicate'].items()):result=v['model']
 return result
oldchecks=0;newchecks=0
for f in (O/'before/assets/minecraft/models/item').glob('*.json'):
 old=json.loads(f.read_text());new=json.loads((R/f.relative_to(O/'before')).read_text())
 for cmd in {int(x['predicate'].get('custom_model_data',0)) for x in old.get('overrides',[])}|{0}:
  for pulling,pull in [(0,0),(1,0),(1,.5),(1,.7),(1,.95),(1,1)]:assert select(old,cmd,pulling,pull)==select(new,cmd,pulling,pull),(f.name,cmd,pulling,pull);oldchecks+=1
for c in m['cosmetics']:
 for target in c['targets']:
  d=json.loads((R/'assets/minecraft/models/item'/(target+'.json')).read_text());assert select(d,c['cmd'])==c['model'];newchecks+=1
  if target=='bow':
   for pull,idx in [(0,1),(.5,1),(.65,2),(.8,2),(.9,3),(1,3)]:assert select(d,c['cmd'],1,pull)==c['overrides'][idx]['model'];newchecks+=1
with zipfile.ZipFile(R/'dist/resource-pack.zip') as z:
 for name,digest in m['asset_sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
 for name in m['asset_sha256']:
  if '/models/item/cosmetic/' not in name or not name.endswith('.json'):continue
  d=json.loads(z.read(name))
  for texture in d.get('textures',{}).values():
   if not texture.startswith('#'):assert 'assets/'+texture.replace(':','/textures/',1)+'.png' in z.namelist(),(name,texture)
cosmetics=json.loads((D/'cosmetic.additions.json').read_text())['content'];skins=json.loads((D/'pokemon-skin.additions.json').read_text())['content'];lines=json.loads((D/'skin-dex.additions.json').read_text())['content']
assert len(cosmetics)==19 and len(skins)==24 and len(lines)==1
line=lines['shadow-2026'];assert set(line['skins'])==set(skins)
for file,new in [('cosmetic',cosmetics),('pokemon-skin',skins),('skin-dex',lines)]:assert not set(new)&set(json.loads((O/'live-config'/(file+'.json')).read_text())['content'])
manifest=json.loads((R/'reports/shadow-20260910/manifest.json').read_text())
for skin in skins.values():
 variants=[v for row in manifest['forms'] if row['species']==skin['pokemon'] and not row['form'] for v in row['variations']]
 for aspect in [skin['aspect'],*line['auras']]:assert any(v['aspects']==[aspect] for v in variants)
result={'cosmetics':len(cosmetics),'pokemon_skins':len(skins),'skindex_collections':len(lines),'existing_item_states_unchanged':oldchecks,'new_item_states_checked':newchecks,'asset_hashes_verified':len(m['asset_sha256']),'overlay_bytes':(R/'dist/resource-pack.zip').stat().st_size,'overlay_sha256':hashlib.sha256((R/'dist/resource-pack.zip').read_bytes()).hexdigest()}
(O/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
