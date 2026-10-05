#!/usr/bin/env python3
"""Import CRE (EproMC) riding data without replacing authored skin rigs.

Content is used with the author's redistribution permission supplied by the operator.

Requires an explicit official Cobblemon reference jar. Prints results to stdout;
never publishes, writes a report, changes the frozen baseline, or deploys data.
"""
import argparse
import collections
import copy
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = '/bedrock/pokemon/models/'
RESOLVER = '/bedrock/pokemon/resolvers/'
SEAT = 'seat_1'


def geometry(doc):
    entries = doc.get('minecraft:geometry', [])
    if len(entries) != 1 or not isinstance(entries[0].get('bones'), list):
        raise ValueError('expected exactly one geometry with a bones array')
    return entries[0]


def seat_reference(doc):
    bones = geometry(doc)['bones']
    by_name = {b['name']: b for b in bones}
    for bone in bones:
        if SEAT not in bone.get('locators', {}):
            continue
        loc = bone['locators'][SEAT]
        offset = loc.get('offset') if isinstance(loc, dict) else loc
        if not isinstance(offset, list) or len(offset) != 3:
            continue
        if bone.get('parent') in by_name and bone['name'].startswith('locator_'):
            parent = by_name[bone['parent']]
            new = copy.deepcopy(bone)
            new['name'] = 'locator_seat_1'
            new['locators'] = {SEAT: copy.deepcopy(loc)}
            # Only the locator, never cubes or unrelated child geometry.
            new = {k: v for k, v in new.items() if k in ('name', 'parent', 'pivot', 'rotation', 'locators')}
        else:
            parent = bone
            new = {'name': 'locator_seat_1', 'parent': bone['name'],
                   'pivot': list(offset), 'locators': {SEAT: copy.deepcopy(loc)}}
        return new, parent.get('pivot', [0, 0, 0])
    return None


def seat_for(doc, reference):
    bones = geometry(doc)['bones']
    if any(SEAT in b.get('locators', {}) for b in bones):
        return None, 'already_seated'
    if not reference:
        return None, 'no_reference_seat'
    seat, ref_pivot = reference
    by_name = {b['name']: b for b in bones}
    parent = by_name.get(seat.get('parent'))
    rule = 'A'
    if parent is None:
        rule = 'B'
        parent = next((by_name[n] for n in ('body', 'torso', 'chest', 'root_body') if n in by_name), None)
        if parent is None:
            roots = [b for b in bones if not b.get('parent') and not b['name'].startswith('locator_')]
            # Multiple roots have no unambiguous main root: do not guess one.
            identifier = geometry(doc).get('description', {}).get('identifier', '').removeprefix('geometry.')
            named = [b for b in roots if b['name'] in (identifier, 'bb_main', 'root', 'main')]
            parent = named[0] if len(named) == 1 else roots[0] if len(roots) == 1 else None
        if parent is None:
            parent = next((b for b in bones if 'body' in b['name'].lower()), None)
    if parent is None:
        return None, 'no_suitable_parent'
    new = copy.deepcopy(seat)
    new['parent'] = parent['name']
    delta = [v - r for v, r in zip(parent.get('pivot', [0, 0, 0]), ref_pivot)]
    new['pivot'] = [v + d for v, d in zip(new.get('pivot', [0, 0, 0]), delta)]
    loc = new['locators'][SEAT]
    if isinstance(loc, dict):
        loc['offset'] = [v + d for v, d in zip(loc['offset'], delta)]
    else:
        new['locators'][SEAT] = [v + d for v, d in zip(loc, delta)]
    name = 'locator_seat_1'
    while name in by_name:
        name += '_cre'
    new['name'] = name
    return new, rule


def append_bone(text, bone):
    """Insert one array element; every pre-existing byte remains in order."""
    original = json.loads(text)
    before = geometry(original)['bones']
    # Locate a structural bones key, not a word inside an escaped JSON string.
    decoder = json.JSONDecoder()
    i = 0
    while i < len(text):
        if text[i] != '"':
            i += 1
            continue
        key, end = decoder.raw_decode(text, i)
        match = re.match(r'\s*:\s*\[', text[end:]) if key == 'bones' else None
        if match:
            start = end + match.end() - 1
            value, finish = decoder.raw_decode(text, start)
            if value == before:
                pos = start + 1
                last = pos
                for _ in value:
                    pos = re.match(r'\s*,?\s*', text[pos:]).end() + pos
                    _, last = decoder.raw_decode(text, pos)
                    pos = last
                addition = (',' if value else '') + json.dumps(bone, separators=(',', ':'), ensure_ascii=False)
                result = text[:last] + addition + text[last:]
                after = json.loads(result)
                assert geometry(after)['bones'] == before + [bone]
                expected = copy.deepcopy(original)
                geometry(expected)['bones'].append(bone)
                assert after == expected
                return result
        i = end
    raise ValueError('cannot locate bones array without rewriting existing content')


def add_property(text, key, value):
    obj = json.loads(text)
    assert key not in obj
    end = text.rfind('}')
    # Insert before trailing whitespace, not after a comment or inside a string.
    pos = end
    while pos and text[pos - 1].isspace():
        pos -= 1
    addition = (',' if obj else '') + '\n  ' + json.dumps(key) + ': ' + json.dumps(value, ensure_ascii=False)
    result = text[:pos] + addition + text[pos:]
    assert json.loads(result) == dict(obj, **{key: value})
    return result


def model_keys(value):
    if isinstance(value, dict):
        for k, v in value.items():
            if k == 'model' and isinstance(v, str):
                yield v if ':' in v else 'cobblemon:' + v
            else:
                yield from model_keys(v)
    elif isinstance(value, list):
        for v in value:
            yield from model_keys(v)


def model_key(path):
    return path.split('/')[1] + ':' + Path(path).name[:-5]


def resources(jar):
    with zipfile.ZipFile(jar) as z:
        return {n: z.read(n) for n in z.namelist() if not n.endswith('/')}


def species_index(files):
    out = {}
    for n, data in files.items():
        if re.match(r'data/[^/]+/species/', n) and n.endswith('.json'):
            doc = json.loads(data)
            out[n.split('/')[1] + ':' + Path(n).stem] = doc
    return out


def behaviour_keys(files):
    # Verify against constants actually present in the reference jar, not a newer checkout.
    keys = set()
    for n, data in files.items():
        if '/riding/behaviour/types/' in n and n.endswith('.class'):
            for key in re.findall(rb'(?:land|air|liquid)/[a-z_]+', data):
                keys.add('cobblemon:' + key.decode())
    return keys


def runtime_updates(cre, root):
    """Import the glider implementation and merge its tick hook with other packs' hooks."""
    paths = ('data/cre/function/tick.mcfunction', 'data/cre/predicate/is_in_air.json',
             'data/cre/predicate/is_riding.json', 'data/minecraft/tags/function/tick.json')
    if not any(p in cre for p in paths):
        return {}
    if not all(p in cre for p in paths):
        raise ValueError('incomplete CRE emergency glider resources')
    result = {p: cre[p] for p in paths}
    tag_path = paths[-1]
    result[tag_path] = (json.dumps(json.loads(cre[tag_path]), indent=2) + '\n').encode()
    existing = Path(root) / tag_path
    if existing.exists():
        tag = json.loads(existing.read_bytes())
        incoming = json.loads(cre[tag_path])
        values = tag.setdefault('values', [])
        for value in incoming['values']:
            identifier = value.get('id') if isinstance(value, dict) else value
            if not any((v.get('id') if isinstance(v, dict) else v) == identifier for v in values):
                values.append(value)
        result[tag_path] = (json.dumps(tag, indent=2) + '\n').encode()
    return {p: b for p, b in result.items()
            if not (Path(root) / p).exists() or (Path(root) / p).read_bytes() != b}


def run(cre_jar, stock_jar, root=ROOT, extra_assets=(), legacy_seat_jars=()):
    root = Path(root)
    stock = resources(stock_jar)
    cre = resources(cre_jar)
    version = json.loads(stock.get('fabric.mod.json', b'{}')).get('version', 'unknown')
    species = species_index(stock)
    stock_species = copy.deepcopy(species)
    species.update(species_index({p.relative_to(root).as_posix(): p.read_bytes()
                                 for p in (root / 'data').rglob('*.json')}))
    allowed = behaviour_keys(stock)
    if not allowed:
        raise ValueError('no riding behaviour constants in stock jar')
    stats = {'stock_version': version, 'species_added': [], 'species_skipped': {},
             'models_copied_cre': [], 'our_models_patched': [], 'rule_A': [], 'rule_B': [],
             'stock_models_copied_for_seats': [], 'no_seat': [], 'changed_files': []}
    effective = dict(stock)
    # Optional official form packs can supply geometry referenced by our authored resolvers.
    # Index only geometry here; do not enable unrelated built-in resolver sets.
    for n, data in stock.items():
        if n.startswith('resourcepacks/') and '/assets/' in n and MODEL in n:
            path = 'assets/' + n.split('/assets/', 1)[1]
            effective.setdefault(path, data)
    for directory in extra_assets:
        directory = Path(directory)
        for p in (directory / 'assets').rglob('*'):
            if p.is_file():
                effective[p.relative_to(directory).as_posix()] = p.read_bytes()
    effective.update({p.relative_to(root).as_posix(): p.read_bytes()
                      for p in (root / 'assets').rglob('*') if p.is_file()})
    own = collections.defaultdict(list)
    for p in (root / 'assets').glob('*/bedrock/pokemon/models/**/*.json'):
        own[model_key(p.relative_to(root).as_posix())].append(p)
    duplicates = {k: sorted(str(p) for p in v) for k, v in own.items() if len(v) > 1}
    additions = {}
    for p in (root / 'data').glob('*/species_additions/**/*.json'):
        doc = json.loads(p.read_bytes())
        targets = doc.get('target', [])
        for target in [targets] if isinstance(targets, str) else targets:
            additions.setdefault(target, []).append((p, doc))
    def write(path, data):
        path = Path(path)
        if path.exists() and path.read_bytes() == data:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        rel = path.relative_to(root).as_posix()
        effective[rel] = data
        stats['changed_files'].append(rel)
    for n, data in sorted(cre.items()):
        if '/species_additions/' not in n or not n.endswith('.json'):
            continue
        doc = json.loads(data)
        target = doc.get('target')
        reason = None
        riding = doc.get('riding', {})
        if not isinstance(target, str) or target not in species:
            reason = 'invalid_target'
        elif not riding.get('seats') or not riding.get('behaviours') or any(
                b.get('key') not in allowed for b in riding['behaviours'].values()):
            reason = 'invalid_riding_behaviour_or_seats'
        elif any('riding' in d for _, d in additions.get(target, [])):
            reason = 'existing_pack_riding'
        elif species[target].get('riding'):
            reason = 'stock_already_rideable' if stock_species.get(target, {}).get('riding') else 'existing_full_species_riding'
        if reason:
            stats['species_skipped'][str(target)] = reason
            continue
        dest = root / ('data/' + target.split(':')[0] + '/species_additions/' + target.split(':')[1] + '.json')
        old = dest.read_text() if dest.exists() else json.dumps({'target': target}) + '\n'
        old_doc = json.loads(old)
        if old_doc.get('target') != target:
            stats['species_skipped'][target] = 'conflicting_destination_target'
            continue
        new = add_property(old, 'riding', riding)
        write(dest, new.encode())
        additions.setdefault(target, []).append((dest, json.loads(new)))
        stats['species_added'].append(target)
    rideable = {s for s, d in species.items() if d.get('riding') or any(f.get('riding') for f in d.get('forms', []))}
    rideable.update(s for s, ds in additions.items() if any(d.get('riding') or any(f.get('riding') for f in d.get('forms', [])) for _, d in ds))
    resolver_models = collections.defaultdict(set)
    for n, data in sorted(effective.items()):
        if RESOLVER in n and n.endswith('.json'):
            d = json.loads(data)
            s = d.get('species')
            if s in rideable:
                resolver_models[s].update(model_keys(d))
    required = set().union(*resolver_models.values()) if resolver_models else set()
    cre_models = {model_key(n): (n, json.loads(data)) for n, data in cre.items() if MODEL in n and n.endswith('.geo.json')}
    references = {k: seat_reference(d) for k, (_, d) in cre_models.items()}
    legacy_references = {}
    for jar in legacy_seat_jars:
        for n, data in sorted(resources(jar).items()):
            if MODEL in n and n.endswith('.json'):
                ref = seat_reference(json.loads(data))
                if ref:
                    canonical = 'assets/' + n.split('/assets/', 1)[1] if '/assets/' in n else n
                    legacy_references.setdefault(model_key(canonical), ref)
    stock_references = {}
    for n, data in sorted(stock.items()):
        if MODEL in n and n.endswith('.json'):
            ref = seat_reference(json.loads(data))
            if ref:
                stock_references[model_key(n)] = ref
    # CRE base files are used only when at least one rideable resolver can render them.
    for key, (n, doc) in sorted(cre_models.items()):
        if key not in required:
            continue
        if key not in own:
            for bone in geometry(doc)['bones']:
                if bone.get('locators') == {}:
                    del bone['locators']
            write(root / n, (json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n').encode())
            own[key].append(root / n)
            stats['models_copied_cre'].append(n)
        else:
            for p in sorted(own[key]):
                text = p.read_bytes().decode()
                bone, rule = seat_for(json.loads(text), references.get(key))
                if bone:
                    write(p, append_bone(text, bone).encode())
                    stats['our_models_patched'].append(p.relative_to(root).as_posix())
    model_files = collections.defaultdict(list)
    for n, data in sorted(effective.items()):
        if MODEL in n and n.endswith('.json'):
            model_files[model_key(n)].append((n, data))
    # Prefer authored reference locators, then CRE's reference, then stock locators.
    species_refs = {}
    for s, keys in sorted(resolver_models.items()):
        preferred = sorted(keys, key=lambda k: (k.split(':')[-1] != s.split(':')[-1] + '.geo', k))
        for key in preferred:
            refs = [seat_reference(json.loads(p.read_bytes())) for p in own.get(key, [])]
            refs += [references.get(key), stock_references.get(key)]
            refs += [seat_reference(json.loads(data)) for _, data in model_files.get(key, [])]
            ref = next((x for x in refs if x), None)
            if ref:
                species_refs[s] = ref
                break
    for s, keys in sorted(resolver_models.items()):
        if s not in species_refs:
            preferred = sorted(keys, key=lambda k: (k.split(':')[-1] != s.split(':')[-1] + '.geo', k))
            ref = next((legacy_references[k] for k in preferred if k in legacy_references), None)
            if ref:
                species_refs[s] = ref
    touched_keys = set()
    for s, keys in sorted(resolver_models.items()):
        if not keys:
            stats['no_seat'].append({'species': s, 'reason': 'no_resolver_models'})
        for key in sorted(keys):
            if key in touched_keys:
                continue
            touched_keys.add(key)
            candidates = [(p.relative_to(root).as_posix(), p.read_bytes()) for p in own.get(key, [])] or model_files.get(key, [])
            if not candidates:
                stats['no_seat'].append({'species': s, 'model': key, 'reason': 'missing_model'})
                continue
            ref = references.get(key) or stock_references.get(key) or legacy_references.get(key) or species_refs.get(s)
            for n, data in candidates:
                doc = json.loads(data)
                bone, rule = seat_for(doc, ref)
                if rule == 'already_seated':
                    continue
                if not bone:
                    stats['no_seat'].append({'species': s, 'model': key, 'path': n, 'reason': rule})
                    continue
                if not own.get(key):
                    stats['stock_models_copied_for_seats'].append(n)
                write(root / n, append_bone(data.decode(), bone).encode())
                stats['rule_' + rule].append({'species': s, 'model': key, 'path': n, 'parent': bone['parent']})
    for s in sorted(rideable - set(resolver_models)):
        stats['no_seat'].append({'species': s, 'reason': 'no_resolver_models'})
    after = collections.defaultdict(list)
    for p in (root / 'assets').glob('*/bedrock/pokemon/models/**/*.json'):
        after[model_key(p.relative_to(root).as_posix())].append(p)
    assert {k: sorted(str(p) for p in v) for k, v in after.items() if len(v) > 1} == duplicates, 'new duplicate model keys'
    uncovered = {x.get('model') for x in stats['no_seat']}
    for key in sorted(required):
        entries = [(str(p), p.read_bytes()) for p in after.get(key, [])] or model_files.get(key, [])
        assert entries or key in uncovered
        for n, data in entries:
            assert seat_reference(json.loads(data)) or key in uncovered, ('seat coverage', key, n)
    for n, data in runtime_updates(cre, root).items():
        write(root / n, data)
    for n in stats['changed_files']:
        if not n.endswith('.json'):
            continue
        d = json.loads((root / n).read_bytes())
        if MODEL in n:
            geometry(d)
    stats['rideable_species'] = len(rideable)
    stats['required_model_keys'] = len(required)
    stats['unchanged_duplicate_keys'] = sorted(duplicates)
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cre_jar', type=Path)
    parser.add_argument('--stock-jar', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--extra-assets', type=Path, action='append', default=[])
    parser.add_argument('--legacy-seat-jar', type=Path, action='append', default=[],
                        help='Read seat locators only from an older mod jar; never import its geometry or data')
    args = parser.parse_args()
    result = run(args.cre_jar, args.stock_jar, args.root, args.extra_assets, args.legacy_seat_jar)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
