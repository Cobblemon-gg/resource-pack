#!/usr/bin/env python3
"""Verify the MSD 1.8 port's isolated resources and retained legacy skin inheritance."""
import json,re,hashlib
from pathlib import Path
from msd18_skin_guards import check
ROOT=Path(__file__).resolve().parents[1]

def main():
    check(ROOT)
    report=json.loads((ROOT/'reports/mega-showdown-1.8-port.json').read_text())
    a=ROOT/'assets/cobblemon/bedrock/pokemon'
    docs=[json.loads(p.read_text()) for p in (a/'resolvers').rglob('*.json')]
    skin_checks=0; variants=0
    for update in report['updates']:
        current=json.loads((ROOT/update['resolver']).read_text());old=report['legacy_resolvers'][update['resolver']]
        assert current['variations'][:len(old['variations'])]==old['variations'],update['resolver']
        added=current['variations'][len(old['variations']):];variants+=len(added)
        for d in docs:
            if d.get('species',d.get('name'))!=update['species']:continue
            for v in d['variations']:
                blockers=set(v.get('aspects',[])) & set(update['protected_aspects'])
                if not blockers:continue
                for nv in added:
                    assert any("!q.has_aspect('"+s+"')" in nv.get('condition','') for s in blockers)
                skin_checks+=1
        # Default and shiny always have a complete isolated model/poser/texture set.
        for shiny in (False,True):
            aspects=set(update['form'])|({'shiny'} if shiny else set());effective={}
            for v in added:
                if set(v.get('aspects',[]))<=aspects:effective.update(v)
            for k in ('model','poser','texture'):assert 'atlas_msd18' in effective[k],(update['species'],k)
    models={p.name.removesuffix('.json') for p in (a/'models/atlas_msd18').glob('*.json')}
    posers={p.stem for p in (a/'posers/atlas_msd18').glob('*.json')}
    animations={k for p in (a/'animations/atlas_msd18').glob('*.json') for k in json.loads(p.read_text())['animations']}
    literal_refs=0
    for p in (a/'posers/atlas_msd18').glob('*.json'):
        s=p.read_text()
        refs=re.findall(r"bedrock(?:_\w+)?\(\s*'([\w]+)'\s*,\s*'([\w]+)'",s)+re.findall(r'bedrock\(\s*(atlas_msd18_\w+)\s*,\s*(\w+)\s*\)',s)
        for g,n in refs:assert 'animation.'+g+'.'+n in animations,(p,g,n)
        literal_refs+=len(refs)
    for d in docs:
        for v in d['variations']:
            for key,inventory in [('model',models),('poser',posers)]:
                if 'atlas_msd18' in v.get(key,''):assert v[key].split(':')[1] in inventory
    for path,info in report['files'].items():
        assert not any(s in path for s in ('crowned','primal','zacian','zamazenta','kyogre','groudon')),path
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==info['sha256'],path
    sound_events={}
    for root in (ROOT.parent/'cobblemon/common/src/main/resources',ROOT):
        sound_events.update(json.loads((root/'assets/cobblemon/sounds.json').read_text()))
    sound_refs=0
    for p in (a/'animations/atlas_msd18').glob('*.json'):
        for animation in json.loads(p.read_text())['animations'].values():
            for event in animation.get('sound_effects',{}).values():
                for e in (event if isinstance(event,list) else [event]):
                    assert e['effect'].removeprefix('cobblemon:') in sound_events,(p,e)
                    sound_refs+=1
    result={'sound_event_references':sound_refs,'updated_sets' :len(report['updates']),'new_variations':variants,'legacy_variations_protected':skin_checks,'literal_animation_references':literal_refs,'models':len(models),'posers':len(posers),'status':'passed'}
    (ROOT/'reports/mega-showdown-1.8-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
