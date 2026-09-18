#!/usr/bin/env python3
"""Port verified eye locators only; preserve local artwork, UVs and legacy rigs."""
from pathlib import Path
import json, subprocess, copy, hashlib
ROOT=Path(__file__).resolve().parents[1]; UP=ROOT.parent/'CobblemonMegaShowdown'; REPORT=ROOT/'reports/mega-showdown-18dfa756'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bones(d):return {b['name']:b for b in d['minecraft:geometry'][0]['bones']}
def clean(b):return {k:v for k,v in b.items() if k!='locators'}
def ancestors_match(name, old, local):
    first=True
    while name:
        if name not in old or name not in local:return False
        a=clean(old[name]); b=clean(local[name])
        if not first:
            a={k:v for k,v in a.items() if k!='cubes'}; b={k:v for k,v in b.items() if k!='cubes'}
        if a!=b:return False
        name=old[name].get('parent'); first=False
    return True
def main():
    assert not (REPORT/'port.json').exists(), 'Port already recorded; validate instead of replacing before snapshots'
    paths=subprocess.check_output(['git','diff','--name-only','837be205..18dfa756'],cwd=UP,text=True).splitlines()
    locals=[(p,load(p)) for p in (ROOT/'assets/cobblemon/bedrock/pokemon/models').rglob('*.geo.json')]
    before={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'assets').rglob('*') if p.is_file()}
    result={'base':'837be205','head':'18dfa756','before_asset_hashes':before,'baseline_sha256':sha(ROOT/'client-baseline.json'),'client_archive_sha256':sha(ROOT.parent/'atlas/client/resource-pack/atlas-baseline.zip'),'updates':[],'skipped':[]}
    for source in paths:
        if not source.endswith('.geo.json'):continue
        assert not any(x in source.lower() for x in ['crowned','primal'])
        old=json.loads(subprocess.check_output(['git','show','837be205:'+source],cwd=UP));new=load(UP/source);ob=bones(old);nb=bones(new);touched=[]
        for target,local in locals:
            lb=bones(local)
            exact=set(ob)<=set(lb) and all(clean(v)==clean(lb[k]) for k,v in ob.items())
            if not exact and target.name!=Path(source).name:continue
            additions=[];replacements={}
            for name,b in nb.items():
                if name not in ob and b.get('locators') and not b.get('cubes') and name not in lb:
                    if ancestors_match(b.get('parent'),ob,lb):additions.append(copy.deepcopy(b))
                elif name in ob and ob[name]!=b and name in lb:
                    if not b.get('cubes') and b.get('locators') and clean(lb[name])==clean(ob[name]) and ancestors_match(b.get('parent'),ob,lb):
                        replacements[name]=copy.deepcopy(b)
                    elif ob[name].get('locators')!=b.get('locators') and ancestors_match(name,ob,lb):
                        v=copy.deepcopy(lb[name]);v['locators']=copy.deepcopy(b.get('locators',{}));replacements[name]=v
            bounds={k:v for k,v in new['minecraft:geometry'][0]['description'].items() if k.startswith('visible_bounds') and v!=old['minecraft:geometry'][0]['description'].get(k)} if exact else {}
            if not additions and not replacements and not bounds:continue
            relative=str(target.relative_to(ROOT));backup=REPORT/'before'/relative;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(target.read_bytes())
            geom=local['minecraft:geometry'][0];geom['bones']=[replacements.get(b['name'],b) for b in geom['bones']]+additions;geom['description'].update(bounds)
            target.write_text(json.dumps(local,indent=2)+'\n')
            result['updates'].append({'source':source,'target':relative,'exact_geometry':exact,'added_bones':[b['name'] for b in additions],'changed_bones':list(replacements),'bounds':bounds,'after_sha256':sha(target)})
            touched.append(relative)
        if not touched:
            candidates=[str(p.relative_to(ROOT)) for p,d in locals if p.name==Path(source).name]
            result['skipped'].append({'source':source,'local_candidates':candidates,'reason':'Different legacy rig; no matching eye parent and ancestor geometry' if candidates else 'No matching local geometry; upstream form not imported'})
    result['notes']=['No cubes, UVs, artwork, resolver selections or texture dependencies changed.','Suicune added left_eye2/left_eye3 duplicate visible cubes omitted; zero-rotation pivot cleanup in Suicune and Mega Eternal Floette is visually neutral and omitted.','Aegislash blade2 poser unused by local pack and Atlas; official 1.8 uses aegislash poser.','Four Mega Metagross textures deleted upstream retained because local resolvers still reference them.']
    (REPORT/'port.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'updated_assets':len(result['updates']),'upstream_models_ported':len({r['source'] for r in result['updates']}),'skipped':len(result['skipped'])}))
if __name__=='__main__':main()
