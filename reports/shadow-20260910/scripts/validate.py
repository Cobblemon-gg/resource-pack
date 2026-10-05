from inventory import *
import hashlib
m=json.loads((P/'reports/shadow-20260910/manifest.json').read_text()); issues=[];warnings=[]
# Add the authored shadow assets above existing resources.
for path,expected in m['asset_sha256'].items():
 f=P/path;assert hashlib.sha256(f.read_bytes()).hexdigest()==expected
 if f.suffix=='.json':
  d=json.loads(f.read_text());id=f.name[:-5]
  if '/models/' in path:models[id]=(d,path)
  if '/posers/' in path:posers[id]=(d,path)
  if '/animations/' in path:anims[f.name.removesuffix('.animation.json')]=(d,path)
compiled=json.loads((R/'atlas/output/model-repairs-20260908/audit/compiled-posers.json').read_text())['posers']
def strings(o):
 if isinstance(o,str):yield o
 elif isinstance(o,list):
  for x in o:yield from strings(x)
 elif isinstance(o,dict):
  for x in o.values():yield from strings(x)
def tex(t):
 if isinstance(t,dict):
  assert t['frames'] and t['fps']>0
  for f in t['frames']:tex(f)
 elif isinstance(t,str):assert (P/('assets/'+t.replace(':','/',1))).is_file(),t
factory={'look':(0,['head']),'pitch_tilt':(0,['root']),'biped_walk':(2,['leg_left','leg_right']),'quadruped_walk':(2,['leg_front_left','leg_front_right','leg_back_left','leg_back_right']),'bimanual_swing':(2,['arm_left','arm_right']),'sine_wing_flap':(4,['wing_left','wing_right'])}
for row in m['forms']:
 label=row['alias']
 for var in row['variations']:
  md=models[var['model'].split(':')[1]][0];boneobjects=md['minecraft:geometry'][0]['bones'];bn=bones(md);assert len(bn)==len(boneobjects)
  assert all(not b.get('parent') or b['parent'] in bn for b in boneobjects)
  tex(var['texture'])
  for layer in var['layers']:
   if layer.get('enabled',True):tex(layer['texture'])
  pid=var['poser'].split(':')[1]
  if pid in posers:
   pd=posers[pid][0];root=pd['rootBone'];assert root in bn,(label,root,sorted(bn));relevant=(bn-{root})|{'__root'}
   for pose in pd['poses'].values():
    for t in pose.get('transformedParts',[]):
     if t['part'] not in relevant:issues.append([label,'transformed',t['part']])
   for expr in strings(pd):
    for name,args in re.findall(r'(?:q|query)\.(look|pitch_tilt|biped_walk|quadruped_walk|bimanual_swing|sine_wing_flap)\(([^()]*)\)',expr):
     params=[x.strip() for x in args.split(',')] if args.strip() else [];offset,defaults=factory[name]
     for idx,default in enumerate(defaults):
      arg=params[offset+idx] if len(params)>offset+idx else repr(default)
      if arg.startswith(("'",'"')) and arg[1:-1] not in relevant:issues.append([label,'factory',name+':'+arg])
    for group,anim in re.findall(r"(?:q|query)\.bedrock\w*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",expr):
     if group=='dummy':continue
     assert group in anims,(label,group)
     animations={k.split('.')[-1]:v for k,v in anims[group][0]['animations'].items()}
     if anim not in animations:issues.append([label,'animation',group+':'+anim])
     else:
      missing=set(animations[anim].get('bones',{}))-bn
      if missing:warnings.append([label,anim,sorted(missing)])
  else:
   parts=compiled.get(var['poser'],{}).get('required_literal_parts')
   if not parts:
    src=next((R/'cobblemon/common/src/main/kotlin').rglob(row['species'].capitalize()+'Model.kt'))
    parts=re.findall(r'(?:getPart|registerChildWithAllChildren)\("([^"]+)"\)',src.read_text())
   missing=set(parts)-bn
   if missing:issues.append([label,'compiled',sorted(missing)])
result={'forms':len(m['forms']),'variants':sum(len(x['variations']) for x in m['forms']),'issues':sorted({json.dumps(i) for i in issues}),'optional_animation_channels_absent':sorted({json.dumps(i) for i in warnings})}
(P/'reports/shadow-20260910/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not issues
