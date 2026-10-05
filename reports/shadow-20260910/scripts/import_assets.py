from inventory import *
import copy,hashlib,shutil
B=P/'assets/cobblemon';written={};manifest=[]
prior=json.loads((P/'reports/shadow-20260910/manifest.json').read_text())['asset_sha256']
def emit(rel,value):
 p=B/rel; p.parent.mkdir(parents=True,exist_ok=True)
 b=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode()
 if p.exists() and str(p) not in written:assert p.read_bytes()==b or prior.get(str(p.relative_to(P)))==hashlib.sha256(p.read_bytes()).hexdigest(),'Refusing conflicting existing asset '+str(p)
 p.write_bytes(b);written[str(p.relative_to(P))]=hashlib.sha256(b).hexdigest()
def pngref(name):return 'cobblemon:textures/pokemon/atlas_shadow/'+name
for style in [1,2]:
 for frame in range(1,13):
  name=f'ef_shadow_512x512_{style}_{frame}.png';src=S/f'ef_shadow/ef_shadow_512x512_{style}'/name
  emit('textures/pokemon/atlas_shadow/auras/'+name,src.read_bytes())
for row in rows:
 sp,form=row['species'],row['form'];source=Path(row['source']);stem=source.name.replace('.geo.json','').replace('.json','');label=sp+('_'+form.replace('-','_') if form else '');alias='atlas_shadow_'+label
 md=json.loads(source.read_text());aura=source.parent/next(x.name for x in source.parent.iterdir() if x.is_dir() and x.name.startswith('ef_'))/('ef_'+source.name)
 assert aura.exists(),aura
 ad=json.loads(aura.read_text());assert len(md['minecraft:geometry'])==len(ad['minecraft:geometry'])==1
 # Align the supplied aura root name with its skin (Mega Staraptor has different root names).
 base_root=next(b['name'] for b in md['minecraft:geometry'][0]['bones'] if not b.get('parent'))
 aura_root=next(b['name'] for b in ad['minecraft:geometry'][0]['bones'] if not b.get('parent'))
 if aura_root!=base_root:
  for b in ad['minecraft:geometry'][0]['bones']:
   if b['name']==aura_root:b['name']=base_root
   if b.get('parent')==aura_root:b['parent']=base_root
 # Preserve supplied cubes, UVs, pivots and rotations.

 for d,suffix in [(md,''),(ad,'_aura')]:
  d['minecraft:geometry'][0]['description']['identifier']='geometry.'+alias+suffix
  emit('bedrock/pokemon/models/atlas_shadow/'+alias+suffix+'.geo.json',d)
 poser=row['base']['poser'];pid=poser.split(':')[1]
 if pid in posers:
  pd=copy.deepcopy(posers[pid][0]);pd['rootBone']=base_root
  if label=='archeops':
   pd=json.loads(json.dumps(pd).replace("'battle_cry'", "'cry'"))
   for pose in pd['poses'].values():
    if 'quirks' in pose:pose['quirks']=[q for q in pose['quirks'] if 'sleep_quirk' not in json.dumps(q)]
  if label=='emboar':pd.get('animations',{}).pop('faint',None) # Official poser references an absent animation; retain default faint behavior.
  text=json.dumps(pd).replace("'mmewtwo_","'mewtwo_")
  groups=set(re.findall(r"(?:q|query)\.bedrock\w*\(\s*['\"]([^'\"]+)['\"]",text))
  for group in sorted(groups):
   if group=='dummy':continue
   assert group in anims,(label,group)
   target=alias+'_'+group.replace('-','_');anim=copy.deepcopy(anims[group][0])
   anim['animations']={'.'.join(k.split('.')[:-2]+[target,k.split('.')[-1]]):v for k,v in anim['animations'].items()}
   emit('bedrock/pokemon/animations/atlas_shadow/'+target+'.animation.json',anim)
   text=text.replace("'"+group+"'","'"+target+"'")
  if label=='gallade_mega':text=text.replace("q.look('head')","q.look('Head')")
  pd=json.loads(text);emit('bedrock/pokemon/posers/atlas_shadow/'+alias+'.json',pd);poser='cobblemon:'+alias
 # Use all supplied shadow texture frames, including the special Arceus emissive pair.
 texturefiles=[f for f in source.parent.glob('*.png') if f.name.startswith(stem.removesuffix('_shadow'))]
 textures={}
 for shiny in [False,True]:
  if sp=='armarouge':names=[f'armarouge_{"shiny_" if shiny else ""}shadow_{i}.png' for i in range(1,5)]
  else:
   prefix=stem.removesuffix('_shadow');names=[prefix+('_shiny_shadow.png' if shiny else '_shadow.png')]
  for name in names:assert (source.parent/name).exists(),name;emit('textures/pokemon/atlas_shadow/'+label+'/'+name,(source.parent/name).read_bytes())
  refs=[pngref(label+'/'+n) for n in names];textures[shiny]=refs[0] if len(refs)==1 else {'frames':refs,'fps':8,'loop':True}
 all_layer_names={l['name'] for _,_,d in resolvers['cobblemon:'+sp] for v in d['variations'] for l in v.get('layers',[]) if 'name' in l}|{'aura'}
 variants=[]
 for kind in ['shadow','shadow-aura1','shadow-aura2']:
  for shiny in [False,True]:
   aspects=([form] if form else [])+[kind]+(['shiny'] if shiny else [])
   layers={name:{'name':name,'enabled':False} for name in sorted(all_layer_names)}
   if sp=='arceus':
    name='arceus_emmisive_'+('shiny_' if shiny else '')+'shadow.png';emit('textures/pokemon/atlas_shadow/'+label+'/'+name,(source.parent/name).read_bytes())
    layers['emissive']={'name':'emissive','enabled':True,'emissive':True,'translucent':True,'texture':pngref(label+'/'+name)}
   if kind!='shadow':
    style=int(kind[-1]);layers['aura']={'name':'aura','enabled':True,'emissive':True,'translucent':True,'texture':{'frames':[pngref(f'auras/ef_shadow_512x512_{style}_{i}.png') for i in range(1,13)],'fps':10,'loop':True}}
   variants.append({'aspects':aspects,'model':'cobblemon:'+alias+('_aura' if kind!='shadow' else '')+'.geo','poser':poser,'texture':textures[shiny],'layers':list(layers.values())})
 manifest.append({'species':sp,'form':form,'alias':alias,'source':str(source),'aura_source':str(aura),'original_poser':row['base']['poser'],'poser':poser,'variations':variants})
# Base variants first, then specific Mega variants. Explicit full definitions replace any inheritance.
for sp in sorted({r['species'] for r in manifest}):
 variants=[v for r in sorted([r for r in manifest if r['species']==sp],key=lambda r:(bool(r['form']),r['form'])) for v in r['variations']]
 order=max([o for o,_,d in resolvers['cobblemon:'+sp]]+[0])+20
 emit('bedrock/pokemon/resolvers/atlas_shadow/atlas_shadow_'+sp+'.json',{'species':'cobblemon:'+sp,'order':order,'variations':variants})
# Retain supplied notices outside assets; source models are included only for shadow variants.
for f in S.rglob('license'):
 dest=P/'reports/shadow-20260910/licenses'/f.parent.name/'license';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
report=P/'reports/shadow-20260910';report.mkdir(parents=True,exist_ok=True)
(report/'manifest.json').write_text(json.dumps({'forms':manifest,'asset_sha256':written},indent=2)+'\n')
commands=['/spawnpokemon '+r['species']+' '+' '.join(v['aspects']) for r in manifest for v in r['variations']]
(report/'spawn-commands.txt').write_text('\n'.join(commands)+'\n')
print('Imported',len(manifest),'model sets,',len({r['species'] for r in manifest}),'species,',len(commands),'variants,',len(written),'assets')
