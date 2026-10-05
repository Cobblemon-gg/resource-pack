#!/usr/bin/env python3
"""Check the 837be205 overlay update and legacy Hoopa priority preservation."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
def main():
    report=json.loads((ROOT/'reports/mega-showdown-1.8-837be205-port.json').read_text())
    before=report['before_asset_hashes']
    after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'assets').rglob('*') if p.is_file()}
    changed={p for p in set(before)|set(after) if before.get(p)!=after.get(p)}
    assert changed<=set(report['files']),changed-set(report['files'])
    assert not set(before)-set(after),'Unexpected asset deletions'
    docs={str(p.relative_to(ROOT)):json.loads(p.read_text()) for p in (ROOT/'assets/cobblemon/bedrock/pokemon/resolvers').rglob('*.json')}
    old=dict(docs);old.update(report['legacy_resolvers'])
    def resolve(source,species,aspects):
        values={};layers={}
        for path,doc in sorted(source.items(),key=lambda x:(x[1].get('order',0),x[0])):
            if doc.get('species',doc.get('name'))!=species:continue
            for v in doc['variations']:
                if not set(v.get('aspects',[]))<=aspects:continue
                blockers=re.findall(r"!q\.has_aspect\('([^']+)'\)",v.get('condition',''))
                if set(blockers)&aspects:continue
                values.update({k:v[k] for k in ['model','poser','texture'] if k in v})
                for layer in v.get('layers',[]):layers[layer.get('name','')]=layer
        return values,{k:v for k,v in layers.items() if v.get('enabled',True)}
    protected=0
    for update in report['updates']:
        species=update['species'];form=set(update['form'])
        for shiny in [set(),{'shiny'}]:
            values,_=resolve(docs,species,form|shiny)
            for k in ['model','poser','texture']:assert 'atlas_msd18' in values[k],(species,form,k,values)
        for doc in old.values():
            if doc.get('species',doc.get('name'))!=species:continue
            for v in doc['variations']:
                aspects=set(v.get('aspects',[]))
                # unbound alone is an ordinary form, not a skin to keep old.
                if not aspects & (set(update['protected_aspects'])-{'unbound'}):continue
                for shiny in [set(),{'shiny'}]:
                    state=aspects|form|shiny
                    assert resolve(old,species,state)==resolve(docs,species,state),(species,state)
                    protected+=1
    for name,scale in [('hoopa_confined',0.7),('hoopa_unbound',2.0)]:
        base=ROOT/'assets/cobblemon/bedrock/pokemon'
        geometry=json.loads((base/'models/atlas_msd18'/('atlas_msd18_'+name+'.geo.json')).read_text())
        roots=[b for b in geometry['minecraft:geometry'][0]['bones'] if not b.get('parent')]
        assert len(roots)==1 and roots[0]['name']==name and roots[0]['pivot']==[0,0,0]
        poser=json.loads((base/'posers/atlas_msd18'/('atlas_msd18_'+name+'.json')).read_text())
        for pose in poser['poses'].values():
            assert {'part':name,'scale':[scale,scale,scale]} in pose['transformedParts']
        animation=json.loads((base/'animations/atlas_msd18'/('atlas_msd18_'+name+'.animation.json')).read_text())
        assert all(name not in v.get('bones',{}) for v in animation['animations'].values())
    manifest=json.loads((ROOT/'client-baseline.json').read_text())
    archive=ROOT.parent/'atlas/client/resource-pack/atlas-baseline.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive_sha256']
    result={'changed_assets':len(changed),'retained_original_assets':len(set(before)-changed),'skin_state_comparisons':protected,'baseline_checksum_unchanged':True,'status':'passed'}
    (ROOT/'reports/mega-showdown-1.8-837be205-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
