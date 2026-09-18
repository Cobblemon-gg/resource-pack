import json,zipfile,pathlib,re,hashlib,collections,itertools
def merge(resources,path,prefix=''):
 with zipfile.ZipFile(path) as z:
  if 'pack.mcmeta' in z.namelist():
   meta=json.loads(z.read('pack.mcmeta'))
   for block in meta.get('filter',{}).get('block',[]):
    for k in list(resources):
     parts=k.split('/',2)
     if len(parts)!=3:continue
     _,ns,rel=parts
     if re.fullmatch(block.get('namespace','.*'),ns) and re.fullmatch(block.get('path','.*'),rel):del resources[k]
  for n in z.namelist():
   if n.startswith(prefix+'assets/') and not n.endswith('/'):
    resources[n[len(prefix):]]=(z.read(n),path.name+':'+n)
def model_json(data):
 # Gson accepts leading/trailing decimal points; normalize numeric tokens only,
 # leaving Molang strings untouched. This prevents silently skipping legacy posers.
 text=data.decode() if isinstance(data,bytes) else data
 pattern=r'"(?:\\.|[^"\\])*"|(?<![\w.])-?\.\d+|(?<![\w.])-?\d+\.(?![\w.])'
 def fix(match):
  token=match[0]
  if token.startswith('"'):return token
  if token.endswith('.'):return token+'0'
  return token.replace('-.','-0.',1) if token.startswith('-.') else '0'+token
 return json.loads(re.sub(pattern,fix,text))

def condition(expr,state):
 if not expr:return True
 if isinstance(expr,bool):return expr
 s=re.sub(r"(?:q|query)\.has_aspect\(['\"]([^'\"]+)['\"]\)",lambda m:str(m[1] in state),str(expr))
 s=s.replace('&&',' and ').replace('||',' or ');s=re.sub(r'!(?!=)',' not ',s).replace('true','True').replace('false','False')
 if re.search(r'[^\s()TrueFalsandort01.]',s):return None
 try:return bool(eval(s,{'__builtins__':{}},{}))
 except:return None
def run(label,pack=None):
 resources={};merge(resources,CORE)
 if label!='official-only':
  
  for mod in sorted((PROFILE/'mods').glob('*.jar')):
   if mod != CORE:merge(resources,mod)
  merge(resources,CLIENT,'resourcepacks/atlas_baseline/')
  # Include selected builtin and local packs, which can add their own form resolvers.
  selected=[]
  options=PROFILE/'options.txt'
  if options.exists():
   for line in options.read_text().splitlines():
    if line.startswith('resourcePacks:'):selected=json.loads(line.split(':',1)[1])
  mod_ids={}
  for jar in (PROFILE/'mods').glob('*.jar'):
   with zipfile.ZipFile(jar) as z:
    if 'fabric.mod.json' in z.namelist():mod_ids[json.loads(z.read('fabric.mod.json'),strict=False).get('id')]=jar
  for selected_pack in selected:
   if selected_pack=='atlas-client:atlas_baseline':continue
   if selected_pack.startswith('file/'):
    file=PROFILE/'resourcepacks'/selected_pack[5:]
    if file.is_file() and zipfile.is_zipfile(file):merge(resources,file)
    elif file.is_dir():
     for file_resource in (file/'assets').rglob('*'):
      if file_resource.is_file():resources[file_resource.relative_to(file).as_posix()]=(file_resource.read_bytes(),str(file_resource))
   elif ':' in selected_pack:
    mod_id,pack_id=selected_pack.split(':',1)
    if mod_id in mod_ids:merge(resources,mod_ids[mod_id],'resourcepacks/'+pack_id+'/')

 if pack:merge(resources,pack)
 docs={};issues=[]
 for n,(b,src) in resources.items():
  if '/bedrock/' in n and n.endswith('.json'):
   try:docs[n]=model_json(b)
   except Exception as e:issues.append(dict(kind='invalid_json',source=src,detail=str(e)))
 models={};posers={};animations={};species=collections.defaultdict(list)
 for n,d in sorted(docs.items()):
  ns=n.split('/')[1];id=ns+':'+pathlib.PurePosixPath(n).name[:-5]
  if '/models/' in n:models[id]=(d,n)
  elif '/posers/' in n:posers[id]=(d,n)
  elif '/animations/' in n:
   for name,a in d.get('animations',{}).items():animations[name]=(a,n)
  elif '/resolvers/' in n and isinstance(d,dict) and 'variations' in d:
   species[d.get('species',d.get('name','unknown'))].append((d.get('order',0),n,d))
 corestates=collections.defaultdict(set)
 with zipfile.ZipFile(CORE) as z:
  for n in z.namelist():
   if '/bedrock/pokemon/resolvers/' in n and n.endswith('.json'):
    d=json.loads(z.read(n));sp=d.get('species',d.get('name'))
    for v in d.get('variations',[]):corestates[sp].add(frozenset(v.get('aspects',[])))
 checks=[];pair_cache={};unknown=set();compiled=set()
 def pair_checks(model,poser):
  key=(model,poser)
  if key in pair_cache:return pair_cache[key]
  found=[]
  def add(kind,detail,source):found.append(dict(kind=kind,detail=detail,source=resources[source][1]))
  if model not in models:return [('missing_model',model)]
  if poser not in posers:
   compiled.add(poser)
   inventory=json.loads(INVENTORY.read_text())['posers'].get(poser)
   if inventory:
    md,mfile=models[model];bones={b['name'] for geo in md.get('minecraft:geometry',[]) for b in geo.get('bones',[])}
    missing=set(inventory['required_literal_parts'])-bones
    roots={b['name'] for geo in md.get('minecraft:geometry',[]) for b in geo.get('bones',[]) if not b.get('parent')}
    missing |= set(inventory.get('required_roots',[]))-roots
    if missing:found.append(dict(kind='compiled_poser_bone_mismatch',detail=', '.join(sorted(missing)),source=inventory['sources'][0]['path']))
   pair_cache[key]=found;return found
  md,mfile=models[model];pd,pfile=posers[poser]
  allbones=[b for geo in md.get('minecraft:geometry',[]) for b in geo.get('bones',[])]
  roots=[b['name'] for b in allbones if not b.get('parent')]
  root=pd.get('rootBone') if pd.get('rootBone') in roots else (pathlib.PurePosixPath(pfile).stem if pathlib.PurePosixPath(pfile).stem in roots else (roots[0] if roots else None))
  bones={'__root'};parents={b['name']:b.get('parent') for b in allbones}
  def descendant(name):
   seen=set()
   while name and name not in seen:
    seen.add(name);name=parents.get(name)
    if name==root:return True
   return False
  bones|={b['name'] for b in allbones if descendant(b['name'])}
  # Animation channels use the geometry, while JSON getPart uses the relevant-parts map.
  animation_bones={b['name'] for b in allbones}
  factories={'look':(0,['head']),'pitch_tilt':(0,['root']), 'biped_walk':(2,['leg_left','leg_right']), 'quadruped_walk':(2,['leg_front_left','leg_front_right','leg_back_left','leg_back_right']), 'bimanual_swing':(2,['arm_left','arm_right']), 'sine_wing_flap':(4,['wing_left','wing_right']), 'punch':(0,['head','body','arm_left','arm_right'])}
  def strings(v):
   if isinstance(v,str):yield v
   elif isinstance(v,list):
    for x in v:yield from strings(x)
   elif isinstance(v,dict):
    for x in v.values():yield from strings(x)
  for text in strings(pd):
   for factory,args in re.findall(r'(?:q|query)\.(look|pitch_tilt|biped_walk|quadruped_walk|bimanual_swing|sine_wing_flap|punch)\(([^()]*)\)',text):
    params=[x.strip() for x in args.split(',')] if args.strip() else []
    offset,defaults=factories[factory]
    for index,default in enumerate(defaults):
     arg=params[offset+index] if len(params)>offset+index else repr(default)
     if len(arg)>1 and arg[0] in "\"'" and arg[-1]==arg[0] and arg[1:-1] not in bones:
      add('animation_factory_bone_missing',factory+': '+arg[1:-1],pfile)
  for name,pose in pd.get('poses',{}).items():
   for part in pose.get('transformedParts',[]):
    if part.get('part') not in bones:add('crash_missing_transformed_bone',name+': '+str(part.get('part')),pfile)
   for expr in pose.get('animations',[]):
    text=expr.get('animation','') if isinstance(expr,dict) else str(expr)
    if isinstance(expr,dict):
     for factory,args in re.findall(r'(?:q|query)\.(look|pitch_tilt|biped_walk|quadruped_walk|bimanual_swing|sine_wing_flap|punch)\(([^()]*)\)',text):
      params=[x.strip() for x in args.split(',')] if args.strip() else []
      offset,defaults=factories[factory]
      for index,default in enumerate(defaults):
       arg=params[offset+index] if len(params)>offset+index else repr(default)
       if len(arg)>1 and arg[0] in "\"'" and arg[-1]==arg[0] and arg[1:-1] not in bones:
        add('crash_conditional_animation_bone_missing',name+': '+factory+': '+arg[1:-1],pfile)

    for group,anim in re.findall(r"(?:q\.)?bedrock(?:_stateful|_quirk)?\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",text):
     if 'animation.'+group+'.'+anim not in animations:add('crash_conditional_animation_missing' if isinstance(expr,dict) else 'missing_animation',name+': '+group+'.'+anim,pfile)
  for group,anim in re.findall(r"(?:q\.)?bedrock(?:_stateful|_quirk)?\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",json.dumps(pd)):
   keya='animation.'+group+'.'+anim
   if keya not in animations:add('missing_animation',keya,pfile)
   else:
    ad,af=animations[keya];missing=set(ad.get('bones',{}))-animation_bones
    if missing:add('animation_bones_absent',keya+': '+', '.join(sorted(missing)),af)
  pair_cache[key]=found;return found
 for sp,sets in species.items():
  ordered=sorted(sets);vs=[(v,n) for _,n,d in ordered for v in d['variations']]
  states={frozenset(v.get('aspects',[])) for v,n in vs}
  states|={s|{'shiny'} for s in list(states)}
  # Every declared variant + normal/shiny, and skin/form combinations are separately labeled.
  declared=set(states);base=corestates[sp];baseuniverse=set().union(*base) if base else set()
  for state in list(states):
   if set(state)-baseuniverse:
    for form in base:
     if not (set(state)&baseuniverse)-{'shiny'}:states.add(state|form)
  for state in sorted(states,key=lambda s:tuple(sorted(s))):
   values={};sources={};layers={};ambiguous=False
   for v,n in vs:
    if not set(v.get('aspects',[]))<=state:continue
    ok=condition(v.get('condition'),state)
    if ok is None:unknown.add(str(v.get('condition')));ambiguous=True;continue
    if not ok:continue
    for k in ['model','poser','texture']:
     if v.get(k) is not None:values[k]=v[k];sources[k]=resources[n][1]
    for layer in v.get('layers',[]):layers[layer.get('name','')]=layer
   row=dict(species=sp,aspects=sorted(state),declared=state in declared,condition_unresolved=ambiguous,assets=values,sources=sources,issues=[])
   for k in ['model','poser']:
    if not values.get(k):row['issues'].append(dict(kind='unresolved_'+k,detail='No matching '+k))
   if values.get('model') and values.get('poser'):
    pc=pair_checks(values['model'],values['poser'])
    for issue in pc:
     row['issues'].append(dict(kind=issue[0],detail=issue[1]) if isinstance(issue,tuple) else issue)
   def texture(t,label):
    if isinstance(t,str):
     if not ':' in t:return
     ns,path=t.split(':',1)
     if 'assets/'+ns+'/'+path not in resources:row['issues'].append(dict(kind='missing_texture',detail=label+': '+t))
    elif isinstance(t,dict):
     for frame in t.get('frames',[]):texture(frame,label)
     if t.get('frames')==[]:row['issues'].append(dict(kind='empty_texture_frames',detail=label))
   if 'texture' in values:texture(values['texture'],'base')
   for name,layer in layers.items():
    if layer.get('enabled',True) is not False:texture(layer.get('texture'),name)
   checks.append(row)
 result=dict(scenario=label,species=len(species),states=len(checks),unique_model_poser_pairs=len(pair_cache),compiled_or_missing_posers=sorted(str(p) for p in compiled),unresolved_conditions=sorted(unknown),parse_issues=issues,checks=checks)
 (OUT/(label+'.json')).write_text(json.dumps(result,indent=2))
 counts=collections.Counter(i['kind'] for r in checks if r['declared'] and not r['condition_unresolved'] for i in r['issues'])
 print(label,'species',len(species),'states',len(checks),'pairs',len(pair_cache),'issues',dict(counts),'conditions',len(unknown),flush=True)
 return result

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description='Audit effective installed Cobblemon assets, including every mod, Atlas baseline and server overlay. Static checks are not an in-game rendering guarantee.')
 parser.add_argument('--profile',type=pathlib.Path,required=True,help='Client instance directory containing mods/')
 parser.add_argument('--overlay',type=pathlib.Path,required=True)
 parser.add_argument('--output',type=pathlib.Path,required=True)
 parser.add_argument('--label',default='installed')
 parser.add_argument('--inventory',type=pathlib.Path,default=pathlib.Path(__file__).parent/'model-audit/compiled-posers.json')
 args=parser.parse_args();PROFILE=args.profile;OUT=args.output;NEW=args.overlay;INVENTORY=args.inventory
 OUT.mkdir(parents=True,exist_ok=True)
 def mod_by_id(identifier):
  matches=[]
  for jar in (PROFILE/'mods').glob('*.jar'):
   with zipfile.ZipFile(jar) as z:
    if 'fabric.mod.json' in z.namelist() and json.loads(z.read('fabric.mod.json'),strict=False).get('id')==identifier:matches.append(jar)
  if len(matches)!=1:raise SystemExit('Expected exactly one '+identifier+' mod: '+str(matches))
  return matches[0]
 CORE=mod_by_id('cobblemon');CLIENT=mod_by_id('atlas-client')
 expected=json.loads(INVENTORY.read_text()).get('cobblemon_jar_sha256')
 if expected!=hashlib.sha256(CORE.read_bytes()).hexdigest():raise SystemExit('Compiled poser inventory does not match this Cobblemon jar; regenerate it before claiming coverage.')
 result=run(args.label,NEW)
 critical={'compiled_poser_bone_mismatch','crash_missing_transformed_bone','crash_conditional_animation_missing','crash_conditional_animation_bone_missing','missing_model','missing_texture'}
 failures=[r for r in result['checks'] if r['declared'] and any(i['kind'] in critical for i in r['issues'])]
 print('Critical/missing-asset states:',len(failures))
 unknown=[p for p in result['compiled_or_missing_posers'] if p not in json.loads(INVENTORY.read_text())['posers']]
 print('Unclassified posers:',unknown,'Parse errors:',len(result['parse_issues']))
 raise SystemExit(bool(failures or unknown or result['parse_issues']))
