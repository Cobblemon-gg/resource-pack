from inventory import *
import hashlib,itertools
manifest=json.loads((P/'reports/shadow-20260910/manifest.json').read_text())
oldstates={};species={x['species'] for x in manifest['forms']}
for sp in species:
 states={frozenset(),frozenset({'shiny'}),frozenset({'alpha'}),frozenset({'female'})}
 for o,n,d in resolvers['cobblemon:'+sp]:
  for v in d['variations']:states.add(frozenset(v.get('aspects',[])))
 oldstates.update({(sp,a):resolve(sp,a) for a in states})
with zipfile.ZipFile(P/'dist/resource-pack.zip') as z:
 for name,digest in manifest['asset_sha256'].items():assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
 for name in z.namelist():
  if '/bedrock/pokemon/resolvers/' in name and name.endswith('.json'):
   d=json.loads(z.read(name));sp=d.get('species');resolvers[sp]=[r for r in resolvers[sp] if r[1]!=name];resolvers[sp].append((d.get('order',0),name,d))
count=0
for row in manifest['forms']:
 for v in row['variations']:
  for extra in [set(),{'alpha'},{'female'},{'alpha','female'}]:
   state=set(v['aspects'])|extra;actual=resolve(row['species'],state)
   for key in ['model','poser','texture']:assert actual[key]==v[key],(row['alias'],state,key,actual[key],v[key])
   expected_layers={l['name']:l for l in v['layers']};actual_layers={l['name']:l for l in actual['layers']}
   assert all(actual_layers[k]==value for k,value in expected_layers.items()),(row['alias'],state)
   assert not [k for k,v in actual_layers.items() if k not in expected_layers and v.get('enabled',True)],(row['alias'],state)
   count+=1
for (sp,state),before in oldstates.items():assert resolve(sp,state)==before,(sp,state,'Existing non-shadow state changed')
result={'shadow_states_checked':count,'existing_states_unchanged':len(oldstates),'zip_asset_hashes_verified':len(manifest['asset_sha256']),'overlay_bytes':(P/'dist/resource-pack.zip').stat().st_size,'overlay_sha256':hashlib.sha256((P/'dist/resource-pack.zip').read_bytes()).hexdigest(),'full_bytes':(P/'dist/resource-pack-full.zip').stat().st_size}
(P/'reports/shadow-20260910/overlay-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
