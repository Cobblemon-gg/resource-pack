#!/usr/bin/env python3
"""Keep newly added legacy skins off the differently UV-mapped MSD 1.8 models."""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def check(root, refresh=False):
    config=root/'tools/msd18-skin-guards.json'
    if not config.exists(): return
    docs={p:json.loads(p.read_text()) for p in (root/'assets/cobblemon/bedrock/pokemon/resolvers').rglob('*.json')}
    errors=[]
    for entry in json.loads(config.read_text()):
        path=root/entry['resolver']; doc=docs[path]
        allowed=set(entry['standard_aspects'])|set(entry['form'])
        blocked=sorted({a for d in docs.values() if d.get('species',d.get('name'))==entry['species']
                        for v in d['variations'] for a in v.get('aspects',[]) if a not in allowed})
        guard=' && '.join("!q.has_aspect('"+a+"')" for a in blocked)
        changed=False
        for v in doc['variations']:
            # Only the imported alias variants are managed; custom skin definitions are never rewritten.
            if set(v.get('aspects',[])) not in [set(a) for a in entry['managed_aspect_sets']]: continue
            if entry.get('asset_prefix', 'atlas_msd18') not in json.dumps({k:x for k,x in v.items() if k!='condition'}): continue
            if v.get('condition','')==guard:continue
            if not refresh:errors.append(str(path.relative_to(root)));break
            if guard:v['condition']=guard
            else:v.pop('condition',None)
            changed=True
        if changed:path.write_text(json.dumps(doc,indent=2)+'\n')
    if errors:raise SystemExit('New skin/form aspects require refreshing MSD legacy guards. Run python3 tools/msd18_skin_guards.py --refresh, then rebuild. Affected resolvers:\n'+'\n'.join(errors))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    check(ROOT,args.refresh)
    print('MSD legacy skin guards '+('refreshed' if args.refresh else 'verified'))
