from pathlib import Path
import json
root=Path(__file__).resolve().parents[2];assets=root/'assets/cobblemon/bedrock/pokemon';changed=[]
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n');changed.append(str(p.relative_to(root)))
# Existing Mega skin geometry uses the head bone, not the new AI pivot.
for mon,num,skin in [('houndoom','0229',''),('altaria','0334','angel')]:
 alias='atlas_compat18_legacy_'+mon+'_mega';p=assets/f'posers/megas/{num}_{mon}/{mon}_mega.json';text=p.read_text().replace("q.look('head_ai')","q.look('head')");d=json.loads(text);d['rootBone']=mon+'_mega'
 write(assets/'posers/atlas_compat18'/f'{alias}.json',d)
 for p in (assets/'resolvers').rglob('*.json'):
  d=json.loads(p.read_text())
  if d.get('species')!='cobblemon:'+mon:continue
  touched=False
  for v in d['variations']:
   model=v.get('model','')
   if 'mega' in v.get('aspects',[]) and ('_hw.geo' in model or '_anniversary' in model or '_angel' in model):v['poser']='cobblemon:'+alias;touched=True
  if touched:write(p,d)
# Pidgeotto's old rig uses the same named limbs as the legacy Pidgeot poser.
# Retain Pidgeotto's own old animations and old portrait/profile framing.
d=json.loads((assets/'posers/atlas_compat18/atlas_compat18_legacy_pidgeot.json').read_text().replace('atlas_compat18_legacy_pidgeot','atlas_compat18_legacy_pidgeotto'))
d.update(rootBone='pidgeotto',portraitScale=2.8,portraitTranslation=[-.4,-.9,0],profileScale=1.1,profileTranslation=[0,.1,0])
write(assets/'posers/atlas_compat18/atlas_compat18_legacy_pidgeotto.json',d)
a=json.loads(Path('/tmp/atlas-old-pidgeotto-animation.json').read_text());a['animations']={k.replace('animation.pidgeotto.','animation.atlas_compat18_legacy_pidgeotto.'):v for k,v in a['animations'].items()}
write(assets/'animations/atlas_compat18/atlas_compat18_legacy_pidgeotto.animation.json',a)
p=assets/'resolvers/pokemon/01_generation/0017_pidgeotto/3_pidgeotto_movie.json';d=json.loads(p.read_text())
for v in d['variations']:
 v['poser']='cobblemon:atlas_compat18_legacy_pidgeotto'
 layers=v.setdefault('layers',[])
 if not any(l.get('name')=='alpha_eyes' for l in layers):layers.append({'name':'alpha_eyes','enabled':False})
write(p,d)
manifest=root/'reports/model-compat-20260910/changed-files.json';prior=json.loads(manifest.read_text());manifest.write_text(json.dumps(sorted(set(prior+changed)),indent=2)+'\n')
