from pathlib import Path
import json,zipfile,subprocess,tarfile,io,re
root=Path(__file__).resolve().parents[2];out=root/'reports/model-compat-20260910'
core=zipfile.ZipFile('/Users/daniel/Library/Application Support/ModrinthApp/profiles/Cobblemon.gg - Ultimate Pokemon Experience (1)/mods/Cobblemon-fabric-1.8.0+1.21.1.jar')
changed=[]
def write(p,d):
 p=root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n');changed.append(str(p.relative_to(root)))
rel='assets/cobblemon/bedrock/pokemon/resolvers/0015_beedrill/0_beedrill_base.json';current=json.loads((root/rel).read_text());base=json.loads(core.read(rel))
mega=[v for v in current['variations'] if 'mega' in v.get('aspects',[])]
for v in mega:v['layers']=[{'name':'alpha_eyes','enabled':False}]
base['variations']+=mega;write(rel,base)
rel='assets/cobblemon/bedrock/pokemon/models/0018_pidgeot/pidgeot.geo.json';write(rel,json.loads(core.read(rel)))
raw=subprocess.check_output(['git','-C',str(root.parent/'cobblemon'),'archive','7e0c490c37','common/src/main/resources/assets/cobblemon/bedrock/pokemon/posers','common/src/main/resources/assets/cobblemon/bedrock/pokemon/animations'])
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
 old={m.name.split('common/src/main/resources/')[1]:json.loads(tar.extractfile(m).read()) for m in tar if m.isfile() and m.name.endswith('.json')}
anims={k:v for p,d in old.items() if '/animations/' in p for k,v in d.get('animations',{}).items()}
rows=json.loads((out/'legacy-compatible.json').read_text());selected=[r for r in rows if (root/r['resolver']).exists()]
# Pidgeot's normal model is restored above; custom models retain their original geometry.
aliases={}
for poser in sorted({r['poser'] for r in selected}):
 name=Path(poser).stem;alias='atlas_compat18_legacy_'+name;d=old[poser];text=json.dumps(d)
 groups=set(re.findall(r"q\.bedrock(?:_[a-z]+)?\(['\"]([^'\"]+)['\"]",text))
 for group in groups:
  newgroup='atlas_compat18_legacy_'+group
  animation={k.replace('animation.'+group+'.','animation.'+newgroup+'.',1):v for k,v in anims.items() if k.startswith('animation.'+group+'.')}
  assert animation,(poser,group)
  write('assets/cobblemon/bedrock/pokemon/animations/atlas_compat18/'+newgroup+'.animation.json',{'format_version':'1.8.0','animations':animation})
  text=text.replace("('"+group+"',", "('"+newgroup+"',")
 write('assets/cobblemon/bedrock/pokemon/posers/atlas_compat18/'+alias+'.json',json.loads(text));aliases[poser]='cobblemon:'+alias
patches={}
for row in selected:
 p=row['resolver'];d=patches.setdefault(p,json.loads((root/p).read_text()));model='cobblemon:'+Path(row['model']).name[:-5]
 for v in d['variations']:
  if v.get('model')==model:
   v['poser']=aliases[row['poser']]
   if set(v.get('aspects',[]))-{'shiny'}:
    layers=v.setdefault('layers',[])
    if not any(l.get('name')=='alpha_eyes' for l in layers):layers.append({'name':'alpha_eyes','enabled':False})
for p,d in patches.items():write(p,d)
(out/'changed-files.json').write_text(json.dumps(sorted(set(changed)),indent=2)+'\n')
print('Updated',len(set(changed)),'files with verified fallback/model/legacy-poser fixes')
