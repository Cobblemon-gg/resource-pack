from pathlib import Path
import json,hashlib,copy
R=Path('/Users/daniel/IdeaProjects/Cobblemon/resource-pack');O=Path('/Users/daniel/IdeaProjects/Cobblemon/atlas/output/shadow-cosmetics-20260910');A=R/'assets/minecraft';configs=json.loads((O/'live-config/cosmetic.json').read_text())['content'];changes={};before={};entries={};mapping=[]
sets=[('shadow_slayer','Shadow Slayer',Path('/Users/daniel/Downloads/Shadow_Slayer Pack/Oraxen Setup/pack'),{'wings':'wing','hat':'hat','hoe':'hoe','pickaxe':'pickaxe','axe':'axe','sword':'sword','shovel':'shovel','bow':'bow','mace':'hammer'}),('shadow_bat_pack','Shadow Bat',Path('/Users/daniel/Downloads/shadow_bat_pack/Oraxen Setup/Oraxen/pack'),{'wings':'wings','hoe':'hoe','pickaxe':'pickaxe','axe':'axe','sword':'sword','shovel':'shovel','bow':'bow','mace':'battle_axe'}),('shadowsteelset','Shadowsteel',Path('/Users/daniel/Downloads/Shadowsteel Set/Oraxen Setup/Oraxen/pack'),{'wings':'wings','hat':'helmet'})]
def write(p,b):
 if not isinstance(b,bytes):b=(json.dumps(b,indent=2)+'\n').encode()
 if p.exists() and p not in before:
  before[p]=p.read_bytes();assert '/models/item/' in str(p) or p.read_bytes()==b,'Existing asset collision '+str(p)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);changes[str(p.relative_to(R))]=hashlib.sha256(b).hexdigest()
def import_model(root,ref,namespace):
 path=ref.split(':')[-1];src=root/'models'/(path+'.json');assert src.exists(),src
 target='item/cosmetic/'+path;dst=A/'models'/(target+'.json')
 if str(dst.relative_to(R)) in changes:return 'minecraft:'+target
 d=json.loads(src.read_text())
 for key,value in list(d.get('textures',{}).items()):
  if value.startswith('#'):continue
  old=value.split(':')[-1];tex=root/'textures'/(old+'.png');assert tex.exists(),tex
  new='item/cosmetic/'+old;write(A/'textures'/(new+'.png'),tex.read_bytes());meta=tex.with_suffix('.png.mcmeta')
  if meta.exists():write(A/'textures'/(new+'.png.mcmeta'),meta.read_bytes())
  d['textures'][key]='minecraft:'+new
 parent=d.get('parent','')
 if parent and (root/'models'/(parent.split(':')[-1]+'.json')).exists():d['parent']=import_model(root,parent,namespace)
 for override in d.get('overrides',[]):override['model']=import_model(root,override['model'],namespace)
 write(dst,d);return 'minecraft:'+target
materials=['wooden','stone','iron','golden','diamond','netherite']
for ns,title,root,wanted in sets:
 for kind,name in wanted.items():
  key=title.lower().replace(' ','-')+'-'+kind;assert key not in configs
  model=import_model(root,ns+'/'+name,ns)
  typ={'hat':'HEAD','wings':'BODY'}.get(kind,kind.upper());item='flint' if kind in ['hat','wings'] else kind if kind in ['bow','mace'] else 'netherite_'+kind
  targets=['flint'] if kind in ['hat','wings'] else [kind] if kind in ['bow','mace'] else [mat+'_'+kind for mat in materials]
  used=set()
  for target in targets:
   p=A/'models/item'/(target+'.json');d=json.loads(p.read_text());used|={int(v['predicate'].get('custom_model_data',0)) for v in d.get('overrides',[])}
  for c in configs.values():
   if c.get('type')==typ or (item=='flint' and c.get('type') in ['HEAD','BODY','LEFT_ARM']):used.add(int(c.get('custom-model-data',0)))
  cmd=max([x for x in used if x<1000]+[0])+1
  additions=[{'predicate':{'custom_model_data':cmd},'model':model}]
  if kind=='bow':
   for i,pull in enumerate([0,0.65,0.9]):
    additions.append({'predicate':{'custom_model_data':cmd,'pulling':1,**({'pull':pull} if pull else {})},'model':import_model(root,ns+'/bow_'+str(i),ns)})
  for target in targets:
   p=A/'models/item'/(target+'.json');d=json.loads(p.read_text());overrides=d.setdefault('overrides',[])
   idx=next((i for i,v in enumerate(overrides) if v['predicate'].get('custom_model_data',0)>cmd),len(overrides));overrides[idx:idx]=copy.deepcopy(additions);write(p,d)
  cosmetic={'type':typ,**({'category':'BACKPACK'} if kind=='wings' else {}),'custom-model-data':cmd,'name':'&#A855F7&l'+title+' '+kind.title(),'description':[' &7• &fShadow Collection'],'icon':{'item':'minecraft:'+item,'customModelData':cmd}}
  entries[key]=cosmetic;configs[key]=cosmetic;mapping.append({'id':key,'source_model':str(root/'models'/ns/(name+'.json')),'model':model,'item':item,'cmd':cmd,'targets':targets,'overrides':additions})
D=R/'reports/shadow-20260910/config-additions';D.mkdir(exist_ok=True)
# JSON is used as an intermediate; serialize YAML below using the local Ruby runtime.
(D/'cosmetic.additions.json').write_text(json.dumps({'content':entries},indent=2))
skins=json.loads((R/'reports/shadow-20260910/manifest.json').read_text())['forms'];species=sorted({r['species'] for r in skins});existing=json.loads((O/'live-config/pokemon-skin.json').read_text())['content']
display={'porygonz':'Porygon-Z','irontreads':'Iron Treads','greattusk':'Great Tusk'}
newskins={sp+'_shadow':{'name':'&#A855F7&lShadow '+display.get(sp,sp.capitalize()),'aspect':'shadow','pokemon':sp} for sp in species}
assert not set(newskins)&set(existing)
(D/'pokemon-skin.additions.json').write_text(json.dumps({'content':newskins},indent=2))
skindex={'name':'&#A855F7&lShadow 2026','display-pokemon':'vaporeon','display-aspect':'shadow','auras':{'shadow-aura1':{'name':'&#A855F7&lShadow Aura I'},'shadow-aura2':{'name':'&#7C3AED&lShadow Aura II'}},'skins':list(newskins),'rewards':[{'type':'AURA','aura':'shadow-aura1','displayName':'&#A855F7&lShadow Aura I'}]}
assert 'shadow-2026' not in json.loads((O/'live-config/skin-dex.json').read_text())['content']
(D/'skin-dex.additions.json').write_text(json.dumps({'content':{'shadow-2026':skindex}},indent=2))
backup=O/'before';backup.mkdir(exist_ok=True)
for p,b in before.items():
 target=backup/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
(O/'manifest.json').write_text(json.dumps({'cosmetics':mapping,'asset_sha256':changes},indent=2))
print('Imported',len(mapping),'cosmetics, prepared',len(newskins),'skin entries and one Skindex collection')
