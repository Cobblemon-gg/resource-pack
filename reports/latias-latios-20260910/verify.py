from pathlib import Path
import json,zipfile,re,itertools
root=Path(__file__).resolve().parents[2]
core=zipfile.ZipFile('/Users/daniel/Library/Application Support/ModrinthApp/profiles/Cobblemon.gg - Ultimate Pokemon Experience (1)/mods/Cobblemon-fabric-1.8.0+1.21.1.jar')
baseline=zipfile.ZipFile(root.parent/'atlas/client/resource-pack/atlas-baseline.zip')
files={p:('zip',core) for p in core.namelist() if p.startswith('assets/') and not p.endswith('/')}
files.update({p:('zip',baseline) for p in baseline.namelist() if p.startswith('assets/') and not p.endswith('/')})
files.update({str(p.relative_to(root)):('file',p) for p in (root/'assets').rglob('*') if p.is_file()})
def read(p):
 kind,src=files[p];return src.read(p) if kind=='zip' else src.read_bytes()
def load(p):return json.loads(read(p))
def lookup(kind,key):
 ns,name=key.split(':',1)
 matches=[p for p in files if p.startswith(f'assets/{ns}/bedrock/pokemon/{kind}/') and p.endswith('/'+name+'.json')]
 assert len(matches)==1,(kind,key,matches)
 return load(matches[0])
res=[]
for p in files:
 if '/resolvers/' in p and ('latias' in p or 'latios' in p) and p.endswith('.json'):
  d=load(p)
  if d.get('species') in ['cobblemon:latias','cobblemon:latios']:res.append((p,d))
results=[];commands=[]
for mon in ['latias','latios']:
 resolvers=sorted([(p,d) for p,d in res if d['species']=='cobblemon:'+mon],key=lambda v:(v[1].get('order',0),v[0]))
 variants={tuple(sorted(v.get('aspects',[]))) for _,d in resolvers for v in d['variations']}
 for aspects0 in sorted(variants):
  for shiny,alpha in itertools.product([False,True],repeat=2):
   aspects=set(aspects0)|({'shiny'} if shiny else set())|({'alpha_eyes'} if alpha else set())
   effective={};layers={}
   for _,d in resolvers:
    for v in d['variations']:
     if set(v.get('aspects',[]))<=aspects:
      effective.update({k:val for k,val in v.items() if k not in ['aspects','layers']})
      for layer in v.get('layers',[]):layers[layer['name']]=layer
   assert all(k in effective for k in ['model','poser','texture']),(mon,aspects,effective)
   model=lookup('models',effective['model']);poser=lookup('posers',effective['poser'])
   bones={b['name'] for b in model['minecraft:geometry'][0]['bones']}
   assert poser['rootBone'] in bones,(mon,aspects,'root',poser['rootBone'])
   for bone in re.findall(r"q\.look\('([^']+)'",json.dumps(poser)):assert bone in bones,(mon,aspects,'look',bone)
   for texture in re.findall(r'cobblemon:textures/[^"\s]+',json.dumps([effective['texture'],[v for v in layers.values() if v.get('enabled',True)]])):
    assert 'assets/cobblemon/'+texture.split(':',1)[1] in files,(mon,aspects,texture)
   skin=next((a for a in aspects if a not in ['mega','shiny','alpha_eyes']),None)
   if skin:assert any(s in effective['model'] for s in ['carnival','demon','angel','greek_2026']),(mon,aspects,effective)
   results.append({'pokemon':mon,'aspects':sorted(aspects),'model':effective['model'],'poser':effective['poser']})
 for aspects in sorted(variants):
  if 'alpha_eyes' in aspects:continue
  commands.append('/spawnpokemon '+mon+' '+' '.join('shiny=true' if a=='shiny' else a for a in aspects))
(root/'reports/latias-latios-20260910/verification.json').write_text(json.dumps(results,indent=2)+'\n')
(root/'reports/latias-latios-20260910/spawn-commands.txt').write_text('\n'.join(commands)+'\n')
print('Verified',len(results),'effective variants: fallback/model/poser/root/look bones and active textures.')
