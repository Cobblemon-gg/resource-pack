#!/usr/bin/env python3
"""Verify the 53022919 Mega Showdown port: isolated resources, references and legacy skin retention."""
from pathlib import Path
import json, hashlib, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from msd18_skin_guards import check
ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT.parent / 'cobblemon/common/src/main/resources/assets/cobblemon'
A = ROOT / 'assets/cobblemon/bedrock/pokemon'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def resolve(source, species, aspects):
    values = {}; layers = {}
    for path, doc in sorted(source.items(), key=lambda x: (x[1].get('order', 0), x[0])):
        if doc.get('species', doc.get('name')) != species: continue
        for v in doc['variations']:
            if not set(v.get('aspects', [])) <= aspects: continue
            if set(re.findall(r"!q\.has_aspect\('([^']+)'\)", v.get('condition', ''))) & aspects: continue
            values.update({k: v[k] for k in ['model', 'poser', 'texture'] if k in v})
            for layer in v.get('layers', []): layers[layer.get('name', '')] = layer
    return values, {k: v for k, v in layers.items() if v.get('enabled', True)}

def texture_exists(ref):
    rel = ref.removeprefix('cobblemon:')
    return (ROOT / 'assets/cobblemon' / rel).exists() or (CORE / rel).exists()

def main():
    check(ROOT)
    report = json.loads((ROOT / 'reports/mega-showdown-1.8-53022919-port.json').read_text())
    before = report['before_asset_hashes']
    after = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'assets').rglob('*') if p.is_file()}
    changed = {p for p in set(before) | set(after) if before.get(p) != after.get(p)}
    assert changed <= set(report['files']), changed - set(report['files'])
    assert not set(before) - set(after), 'Unexpected asset deletions'
    for path, info in report['files'].items():
        assert sha(ROOT / path) == info['sha256'], path
        assert not any(s in path for s in ('crowned', 'primal', 'zacian', 'zamazenta', 'kyogre', 'groudon')), path
    docs = {str(p.relative_to(ROOT)): json.loads(p.read_text()) for p in (A / 'resolvers').rglob('*.json')}
    old = dict(docs); old.update(report['legacy_resolvers'])
    protected = 0; new_variations = 0; texture_refs = 0
    for update in report['updates']:
        species = update['species']; form = set(update['form'])
        current = docs[update['resolver']]; legacy = report['legacy_resolvers'][update['resolver']]
        assert current['variations'][:len(legacy['variations'])] == legacy['variations'], update['resolver']
        added = current['variations'][len(legacy['variations']):]; new_variations += len(added)
        assert added == update['new_variations']
        for v in added:
            if 'atlas_msd18' in json.dumps({k: x for k, x in v.items() if k != 'condition'}):
                assert all("!q.has_aspect('" + a + "')" in v.get('condition', '') for a in update['protected_aspects']), (update['resolver'], v.get('aspects'))
            for ref in [v.get('texture')] + [l.get('texture') for l in v.get('layers', []) if isinstance(l.get('texture'), str)]:
                if ref: assert texture_exists(ref), ref; texture_refs += 1
        for shiny in [set(), {'shiny'}]:
            values, _ = resolve(docs, species, form | shiny)
            for k in ['model', 'poser', 'texture']: assert 'atlas_msd18' in values[k], (species, form, k, values)
        # Forms deliberately updated by this port (e.g. mega-z while checking the base) are not legacy skins to keep old.
        ported_forms = {a for u in report['updates'] if u['species'] == species for a in u['form']}
        for doc in old.values():
            if doc.get('species', doc.get('name')) != species: continue
            for v in doc['variations']:
                aspects = set(v.get('aspects', []))
                if not (aspects - ported_forms) & set(update['protected_aspects']): continue
                for shiny in [set(), {'shiny'}]:
                    state = aspects | form | shiny
                    assert resolve(old, species, state) == resolve(docs, species, state), (species, state)
                    protected += 1
    models = {p.name.removesuffix('.json') for p in (A / 'models/atlas_msd18').glob('*.json')}
    posers = {p.stem for p in (A / 'posers/atlas_msd18').glob('*.json')}
    animations = {k for p in (A / 'animations/atlas_msd18').glob('*.json') for k in json.loads(p.read_text())['animations']}
    literal_refs = 0
    for p in (A / 'posers/atlas_msd18').glob('*.json'):
        s = p.read_text()
        refs = re.findall(r"bedrock(?:_\w+)?\(\s*'([\w]+)'\s*,\s*'([\w]+)'", s)
        for g, n in refs: assert 'animation.' + g + '.' + n in animations, (p.name, g, n)
        literal_refs += len(refs)
        poser = json.loads(s)
        if poser.get('rootBone') and str(p.relative_to(ROOT)) in report['files']:
            geo = json.loads((A / 'models/atlas_msd18' / (p.stem + '.geo.json')).read_text())
            assert any(b['name'] == poser['rootBone'] for b in geo['minecraft:geometry'][0]['bones']), (p.name, poser['rootBone'])
    for d in docs.values():
        for v in d['variations']:
            for key, inventory in [('model', models), ('poser', posers)]:
                if 'atlas_msd18' in v.get(key, ''): assert v[key].split(':')[1] in inventory, v[key]
    sound_events = {}
    for root in (CORE, ROOT / 'assets/cobblemon'):
        sound_events.update(json.loads((root / 'sounds.json').read_text()))
    particle_ids = set()
    for root in (CORE / 'bedrock/particles', ROOT / 'assets/cobblemon/bedrock/particles'):
        for p in root.rglob('*.json'):
            try: particle_ids.add(json.loads(p.read_text())['particle_effect']['description']['identifier'])
            except Exception: pass
    sound_refs = 0; particle_refs = 0; bone_warnings = {}
    for p in (A / 'animations/atlas_msd18').glob('*.json'):
        doc = json.loads(p.read_text())
        geo_path = A / 'models/atlas_msd18' / (p.name.replace('.animation.json', '.geo.json'))
        geo_bones = {b['name'] for b in json.loads(geo_path.read_text())['minecraft:geometry'][0]['bones']} if geo_path.exists() else None
        for animation in doc['animations'].values():
            for event in animation.get('sound_effects', {}).values():
                for e in (event if isinstance(event, list) else [event]):
                    assert e['effect'].removeprefix('cobblemon:') in sound_events, (p.name, e); sound_refs += 1
            for event in animation.get('particle_effects', {}).values():
                for e in (event if isinstance(event, list) else [event]):
                    ident = e['effect'] if ':' in e['effect'] else 'cobblemon:' + e['effect']
                    assert ident in particle_ids, (p.name, e); particle_refs += 1
            if geo_bones is not None:
                missing = set(animation.get('bones', {})) - geo_bones
                if missing: bone_warnings[p.name] = sorted(set(bone_warnings.get(p.name, [])) | missing)
    manifest = json.loads((ROOT / 'client-baseline.json').read_text())
    archive = ROOT.parent / 'atlas/client/resource-pack/atlas-baseline.zip'
    assert sha(ROOT / 'client-baseline.json') == report['baseline_sha256'], 'pack client-baseline.json changed'
    result = {'status': 'passed', 'updated_sets': len(report['updates']), 'new_variations': new_variations, 'skin_state_comparisons': protected,
              'changed_assets': len(changed), 'retained_original_assets': len(set(before) - changed), 'new_variation_texture_references': texture_refs,
              'literal_animation_references': literal_refs, 'sound_event_references': sound_refs, 'particle_references': particle_refs,
              'atlas_msd18_models': len(models), 'atlas_msd18_posers': len(posers), 'pack_manifest_unchanged': True,
              # The Atlas client archive is outside this repository; a mismatch here predates/postdates the port and is reported, not fixed.
              'atlas_client_archive_matches_pack_manifest': sha(archive) == manifest['archive_sha256'],
              'atlas_client_archive_sha256': sha(archive), 'pack_manifest_archive_sha256': manifest['archive_sha256'],
              'animation_bones_absent_from_geometry': bone_warnings}
    (ROOT / 'reports/mega-showdown-1.8-53022919-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'animation_bones_absent_from_geometry'}, indent=2))
    print('animation bone warnings (files):', {k: len(v) for k, v in bone_warnings.items()})

if __name__ == '__main__': main()
