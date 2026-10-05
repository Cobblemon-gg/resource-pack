#!/usr/bin/env python3
"""Conservative, reproducible model audit. Never replace a custom model by resemblance."""
import argparse, collections, hashlib, io, json, subprocess, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'common/src/main/resources/'

def tree(repo, revision):
    data = subprocess.check_output(['git', '-C', str(repo), 'archive', revision, PREFIX + 'assets/cobblemon'])
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        return {m.name[len(PREFIX):]: archive.extractfile(m).read() for m in archive if m.isfile()}

def same(a, b, path):
    if a == b: return True
    if path.endswith('.json'):
        try: return json.loads(a) == json.loads(b)
        except (ValueError, UnicodeError): pass
    return False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cobblemon', type=Path, default=ROOT.parent / 'cobblemon')
    parser.add_argument('--old', default='7e0c490c37')
    parser.add_argument('--new', default='1.8.0')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    old, new = tree(args.cobblemon, args.old), tree(args.cobblemon, args.new)
    source = {str(p.relative_to(ROOT)): p.read_bytes() for p in (ROOT/'assets').rglob('*') if p.is_file() and not p.name.startswith('.')}
    # Resolver variations with custom aspects may inherit geometry/poser from the base.
    custom = collections.defaultdict(list)
    native_by_species = collections.defaultdict(set)
    for np, nd in new.items():
        if '/resolvers/' in np and np.endswith('.json'):
            r = json.loads(nd)
            native_by_species[r.get('species')].update(a for v in r.get('variations', []) for a in v.get('aspects', []))
    for path, data in source.items():
        if '/resolvers/' not in path or not path.endswith('.json'): continue
        d = json.loads(data)
        species = d.get('species', '').split(':')[-1]
        native_aspects = native_by_species[d.get('species')]
        if any(set(v.get('aspects', [])) - native_aspects for v in d.get('variations', [])):
            custom[species].append(path)
    # Pin old base assets for texture-only skins whose inherited base geometry changed.
    # Existing custom geometry is never overwritten. Shared file paths preserve normal pack priority.
    old_models = {Path(p).name: p for p in old if '/pokemon/models/' in p and p.endswith('.geo.json')}
    new_models = {Path(p).name: p for p in new if '/pokemon/models/' in p and p.endswith('.geo.json')}
    local_models = {Path(p).name: p for p in source if '/pokemon/models/' in p and p.endswith('.geo.json')}
    pinned = []
    for species, resolvers in custom.items():
        name = species + '.geo.json'
        if name not in old_models or name not in new_models or name in local_models: continue
        op, np = old_models[name], new_models[name]
        if same(old[op], new[np], op): continue
        inherits = any(any(v.get('texture') and not v.get('model') and v.get('aspects') and v.get('aspects') != ['shiny'] for v in json.loads(source[r]).get('variations', [])) for r in resolvers)
        if not inherits: continue
        # Preserve the entire old base geometry/animation/poser dependency, under upstream paths.
        for p, data in old.items():
            n = Path(p).name
            if '/pokemon/' not in p: continue
            relevant = (n == name or ('/posers/' in p and n == species+'.json') or ('/animations/' in p and n == species+'.animation.json'))
            if '/textures/pokemon/' in p and species in Path(p).parts:
                relevant = True
            if '/resolvers/' in p and p.endswith('.json') and json.loads(data).get('species') == 'cobblemon:'+species:
                relevant = True
            if relevant and p not in source:
                source[p] = data
                pinned.append({'species': species, 'path': p, 'reason': 'texture-only skin inherits changed base geometry'})
                if args.apply:
                    dest=ROOT/p; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
    removed=[]
    for p, data in list(source.items()):
        # Only exact resource paths: deleting different-path resolver files may affect merging/order.
        if p in new and same(data, new[p], p):
            removed.append({'path':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            if args.apply: (ROOT/p).unlink()
            del source[p]
    # The engine resolves geometry/posers by basename. Report collisions across directories too.
    local_models = collections.defaultdict(list)
    for p in source:
        if '/pokemon/models/' in p and p.endswith('.geo.json'): local_models[Path(p).name].append(p)
    rows=[]
    for name,p in sorted(new_models.items()):
        op=old_models.get(name)
        if op and same(old[op],new[p],p): continue
        overrides=local_models.get(name,[])
        rows.append({'model':name.removesuffix('.geo.json'),'upstream_change':'new' if op is None else 'changed','result':'retained custom/legacy model' if overrides else 'uses Cobblemon 1.8 model','upstream_path':p,'pack_paths':overrides})
    report={'old_revision':subprocess.check_output(['git','-C',str(args.cobblemon),'rev-parse',args.old],text=True).strip(),'new_revision':subprocess.check_output(['git','-C',str(args.cobblemon),'rev-parse',args.new],text=True).strip(),'applied':args.apply,'removed_identical':removed,'pinned_legacy':pinned,'models':rows,'custom_skin_species':sorted(custom)}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/cobblemon-1.8-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Cobblemon 1.8 model test checklist','','Generated against release `'+report['new_revision']+'` and pre-update `'+report['old_revision']+'`.','',f'{len(rows)} upstream new/changed geometry files; {sum(r["result"].startswith("uses") for r in rows)} use the 1.8 model; {sum(r["result"].startswith("retained") for r in rows)} retain pack models.',f'{len(removed)} identical resources removed ({sum(r["bytes"] for r in removed):,} raw bytes); {len(pinned)} old dependency files pinned for texture-only skins.','','For every row using 1.8: test normal/shiny, regional/form aspects, walking, idle, swimming/flying, battle, fainting, shoulder/riding where supported, and every owned skin. For retained models: test skins and animations against 1.8; these are deliberately not counted as upgraded geometry. Geometry equality does not prove skin/poser compatibility.','','| Tested | Model | Upstream | Effective geometry |','|---|---|---|---|']
    lines += [f'| [ ] | `{r["model"]}` | {r["upstream_change"]} | {r["result"]} |' for r in rows]
    lines += ['','## Retained inherited skin dependencies','']+[f'- `{x["species"]}`: `{x["path"]}`' for x in pinned]
    lines += ['','## Identical resources removed','']+[f'- `{x["path"]}`' for x in removed]
    (ROOT/'reports/cobblemon-1.8-model-test-list.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'models':len(rows),'using_18':sum(r['result'].startswith('uses') for r in rows),'removed_identical':len(removed),'pinned_dependencies':len(pinned)},indent=2))

if __name__ == '__main__': main()
