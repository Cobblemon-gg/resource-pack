from pathlib import Path
import json,zipfile,re,collections
root=Path(__file__).resolve().parents[2];mods=Path('/Users/daniel/Library/Application Support/ModrinthApp/profiles/Cobblemon.gg - Ultimate Pokemon Experience (1)/mods')
files={};archives=[]
for jar in [mods/'Cobblemon-fabric-1.8.0+1.21.1.jar',mods/'cobblemon-journey-mounts-1.7.2.jar',root.parent/'atlas/client/resource-pack/atlas-baseline.zip']:
 z=zipfile.ZipFile(jar);archives.append(z)
 files.update({p:lambda p=p,z=z:z.read(p) for p in z.namelist() if p.startswith('assets/') and p.endswith('.json')})
files.update({str(p.relative_to(root)):p.read_bytes for p in (root/'assets').rglob('*.json')})
cache={}
def load(p):
 if p not in cache:
  try:cache[p]=json.loads(files[p]())
  except:cache[p]={}
 return cache[p]
indexes={k:{} for k in ['models','posers']};res=collections.defaultdict(list)
for p in files:
 for k in indexes:
  if '/pokemon/'+k+'/' in p:indexes[k][p.split('/')[1]+':'+Path(p).name[:-5]]=p
 if '/pokemon/resolvers/' in p:
  d=load(p)
  if d.get('species'):res[d['species']].append((p,d))
def required(d):return {d.get('rootBone')}|set(re.findall(r"q\.look\(['\"]([^'\"]+)",json.dumps(d)))|set(re.findall(r'"part":\s*"([^\"]+)"',json.dumps(d)))
issues=[]
for species,entries in res.items():
 entries.sort(key=lambda x:(x[1].get('order',0),x[0]))
 options={frozenset(v.get('aspects',[])) for _,d in entries for v in d.get('variations',[]) if not any(a.startswith('!') for a in v.get('aspects',[]))};options.add(frozenset())
 for aspects in options:
  e={};origin=None
  for p,d in entries:
   for v in d.get('variations',[]):
    if all((a[1:] not in aspects if a.startswith('!') else a in aspects) for a in v.get('aspects',[])):
     if 'model' in v:origin=p
     e.update(v)
  mp=indexes['models'].get(e.get('model'));pp=indexes['posers'].get(e.get('poser'))
  if not mp or not pp:continue
  g=load(mp).get('minecraft:geometry',[])
  if not g:continue
  bones={b['name'] for b in g[0].get('bones',[])};missing=required(load(pp))-bones-{None}
  if missing:issues.append({'species':species,'aspects':sorted(aspects),'model':mp,'poser':pp,'resolver':origin,'missing':sorted(missing)})
(root/'reports/model-compat-20260910/audit.json').write_text(json.dumps(issues,indent=2)+'\n')
print('Checked',len(res),'species;',len(issues),'variant mismatches')
for (species,model,poser),items in __import__('itertools').groupby(sorted(issues,key=lambda x:(x['species'],x['model'],x['poser'])),lambda x:(x['species'],x['model'],x['poser'])):
 vals=list(items);print(species,Path(model).name,Path(poser).name,vals[0]['missing'])
