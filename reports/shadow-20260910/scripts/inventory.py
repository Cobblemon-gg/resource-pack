from pathlib import Path
import json,zipfile,re,collections
R=Path('/Users/daniel/IdeaProjects/Cobblemon'); P=R/'resource-pack'; S=Path('/Users/daniel/Downloads/shadow/shadow'); O=R/'atlas/output/shadow-skins-20260910'
profile=Path('/Users/daniel/Library/Application Support/ModrinthApp/profiles/Cobblemon.gg - Ultimate Pokemon Experience (1)/mods')
resources={}
def mergejar(path,prefix=''):
 with zipfile.ZipFile(path) as z:
  for n in z.namelist():
   if n.startswith(prefix+'assets/') and n.endswith('.json'):resources[n[len(prefix):]]=(z.read(n),str(path)+':'+n)
mergejar(profile/'Cobblemon-fabric-1.8.0+1.21.1.jar')
mergejar(R/'atlas/common-fabric/build/libs/atlas-common-fabric-1.3.0.jar')
mergejar(profile/'atlas-client-1.3.0.jar');mergejar(profile/'atlas-client-1.3.0.jar','resourcepacks/atlas_baseline/')
for f in (P/'assets').rglob('*.json'):
 if 'atlas_shadow' in f.parts:continue
 resources[str(f.relative_to(P))]=(f.read_bytes(),str(f))
docs={}
for n,(b,src) in resources.items():
 if '/bedrock/pokemon/' in n:
  try:docs[n]=json.loads(b)
  except ValueError:pass
models={Path(n).name[:-5]:(d,n) for n,d in sorted(docs.items()) if '/models/' in n}
posers={Path(n).name[:-5]:(d,n) for n,d in sorted(docs.items()) if '/posers/' in n}
anims={Path(n).name.removesuffix('.animation.json'):(d,n) for n,d in sorted(docs.items()) if '/animations/' in n}
resolvers=collections.defaultdict(list)
for n,d in docs.items():
 if '/resolvers/' in n and 'variations' in d:resolvers[d.get('species')].append((d.get('order',0),n,d))
def cond(s,a):
 if not s:return True
 s=re.sub(r"(?:q|query)\.has_aspect\(['\"]([^'\"]+)['\"]\)",lambda m:str(m[1] in a),str(s)).replace('&&',' and ').replace('||',' or ')
 s=re.sub(r'!(?!=)',' not ',s).replace('true','True').replace('false','False')
 try:return bool(eval(s,{'__builtins__':{}},{}))
 except:return False
def resolve(sp,a):
 vals={};layers={}
 for order,n,d in sorted(resolvers['cobblemon:'+sp]):
  for v in d['variations']:
   if set(v.get('aspects',[]))<=set(a) and cond(v.get('condition'),a):
    vals.update({k:v[k] for k in ['model','poser','texture'] if k in v})
    layers.update({x['name']:x for x in v.get('layers',[]) if 'name' in x})
 vals['layers']=list(layers.values());return vals
def bones(d):return {b['name'] for g in d['minecraft:geometry'] for b in g['bones']}
rows=[]
for f in sorted(S.rglob('*.json')):
 if '_shadow' not in f.parent.name or f.name.startswith('ef_'):continue
 name=f.name.replace('.geo.json','').replace('.json','').removesuffix('_shadow');sp=name.split('_mega')[0].replace('porygon-z','porygonz');form=name[len(name.split('_mega')[0]):].strip('_').replace('_','-');asp=[form] if form else []
 v=resolve(sp,asp);md=models.get(v.get('model','').split(':')[-1]);sd=json.loads(f.read_text());missing=sorted(bones(md[0])-bones(sd)) if md else ['NO MODEL']
 row={'species':sp,'form':form,'source':str(f),'base':v,'missing_base_bones':missing,'extra_bones':sorted(bones(sd)-bones(md[0])) if md else [],'poser_json':v.get('poser','').split(':')[-1] in posers};rows.append(row)
if __name__=='__main__':
 (O/'inventory.json').write_text(json.dumps(rows,indent=2))
 for x in rows:print(x['species'],x['form'],x['base'].get('model'),x['base'].get('poser'),'json',x['poser_json'],'missing',x['missing_base_bones'])
