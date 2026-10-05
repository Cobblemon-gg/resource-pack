#!/usr/bin/env python3
"""Canonicalize colliding Bedrock IDs so resource-pack priority actually applies."""
import collections, hashlib, json, stat
from pathlib import Path
from audit_cobblemon_18 import ROOT, tree, same

def main():
    report_path=ROOT/'reports/cobblemon-1.8-audit.json'
    report=json.loads(report_path.read_text())
    upstream=tree(ROOT.parent/'cobblemon',report['new_revision'])
    moved=[]; removed=[]; conflicts=[]
    def mutate(source, destination=None):
        mode=source.parent.stat().st_mode
        source.parent.chmod(mode | stat.S_IWUSR)
        try:
            if destination is None: source.unlink()
            else: source.rename(destination)
        finally: source.parent.chmod(mode)
    def journal():
        # Persist each mutation so interruption cannot lose the byte-preservation audit.
        report['canonical_path_moves']=prior_moves + moved
        report['removed_identical']=prior_removed + removed
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    prior_moves=list(report.get('canonical_path_moves',[]))
    prior_removed=list(report['removed_identical'])
    for kind in ('models','posers','animations','resolvers'):
        native=collections.defaultdict(list); local=collections.defaultdict(list)
        for p in upstream:
            if '/bedrock/pokemon/'+kind+'/' in p and p.endswith('.json'): native[Path(p).name].append(p)
        for p in (ROOT/'assets/cobblemon/bedrock/pokemon'/kind).rglob('*.json'): local[p.name].append(p)
        for name,files in local.items():
            if len(native[name])!=1: continue
            np=native[name][0]
            # Resolver names are only comparable when the species is the same.
            if kind=='resolvers': files=[p for p in files if json.loads(p.read_bytes()).get('species')==json.loads(upstream[np]).get('species')]
            if len(files)!=1:
                conflicts.append({'kind':kind,'name':name,'paths':[str(p.relative_to(ROOT)) for p in files]});continue
            p=files[0]; old=p.relative_to(ROOT).as_posix(); data=p.read_bytes(); dest=ROOT/np
            if same(data,upstream[np],np):
                removed.append({'path':old,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'same_as_upstream':np})
                mutate(p)
                journal()
            elif old!=np:
                if dest.exists(): raise RuntimeError(f'Refusing to overwrite {dest}')
                dest.parent.mkdir(parents=True,exist_ok=True);mutate(p,dest)
                moved.append({'from':old,'to':np,'sha256':hashlib.sha256(data).hexdigest()})
                journal()
    journal()
    report['unresolved_same_id_conflicts']=conflicts
    models=collections.defaultdict(list)
    for p in (ROOT/'assets/cobblemon/bedrock/pokemon/models').rglob('*.geo.json'): models[p.name].append(p.relative_to(ROOT).as_posix())
    for row in report['models']:
        row['pack_paths']=models[row['model']+'.geo.json']
        row['result']='retained custom/legacy model' if row['pack_paths'] else 'uses Cobblemon 1.8 model'
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    checklist=ROOT/'reports/cobblemon-1.8-model-test-list.md';s=checklist.read_text()
    # Regenerate table and summary from final effective model IDs.
    a=s.index('| Tested |');b=s.index('\n## ',a)
    table=['| Tested | Model | Upstream | Effective geometry |','|---|---|---|---|']+[f'| [ ] | `{r["model"]}` | {r["upstream_change"]} | {r["result"]} |' for r in report['models']]
    s=s[:a]+'\n'.join(table)+'\n'+s[b:]
    s+='\n## Canonical resource path moves\n\nThe following byte-preserving moves make retained overrides occupy the same resource path as upstream. Cobblemon resolves Bedrock IDs by basename, so two different paths with the same basename otherwise depend on iteration order.\n\n'+'\n'.join('- `'+x['from']+'` → `'+x['to']+'`' for x in report['canonical_path_moves'])+'\n'
    s+='\n## Additional identical Bedrock resources removed\n\n'+'\n'.join('- `'+x['path']+'` (provided by `'+x['same_as_upstream']+'`)' for x in report['removed_identical'] if 'same_as_upstream' in x)+'\n'
    import re
    s=re.sub(r'\d+ identical resources removed \([\d,]+ raw bytes\)',f'{len(report["removed_identical"])} identical resources removed ({sum(x["bytes"] for x in report["removed_identical"]):,} raw bytes)',s)
    checklist.write_text(s)
    print(json.dumps({'moves':len(moved),'extra_duplicates_removed':len(removed),'conflicts':len(conflicts)},indent=2))

if __name__=='__main__':main()
