from pathlib import Path
import json,zipfile
root=Path(__file__).resolve().parents[2]
assets=root/'assets/cobblemon'
jar=Path('/Users/daniel/Library/Application Support/ModrinthApp/profiles/Cobblemon.gg - Ultimate Pokemon Experience (1)/mods/Cobblemon-fabric-1.8.0+1.21.1.jar')
changed=[]
with zipfile.ZipFile(jar) as z:
 for num,mon in [('0380','latias'),('0381','latios')]:
  rel=f'bedrock/pokemon/resolvers/{num}_{mon}/0_{mon}_base.json';p=assets/rel
  existing=json.loads(p.read_text());mega=[v for v in existing['variations'] if 'mega' in v.get('aspects',[])]
  base=json.loads(z.read('assets/cobblemon/'+rel))
  for v in mega:
   v['layers']=[{'name':'alpha_eyes','enabled':False}]
  base['variations']+=mega
  p.write_text(json.dumps(base,indent=2)+'\n');changed.append(str(p.relative_to(root)))
 for p in (assets/'bedrock/pokemon/resolvers/pokemon').rglob('*.json'):
  data=json.loads(p.read_text())
  if data.get('species') not in ('cobblemon:latias','cobblemon:latios'):continue
  mon=data['species'].split(':')[1]
  for v in data['variations']:
   v['poser']='cobblemon:mega_latios' if 'mega' in v.get('aspects',[]) else 'cobblemon:'+mon
   layers=v.setdefault('layers',[])
   if not any(l.get('name')=='alpha_eyes' for l in layers):layers.append({'name':'alpha_eyes','enabled':False})
  p.write_text(json.dumps(data,indent=2)+'\n');changed.append(str(p.relative_to(root)))
(root/'reports/latias-latios-20260910/changed-files.json').write_text(json.dumps(changed,indent=2)+'\n')
print('Updated',len(changed),'resolvers')
