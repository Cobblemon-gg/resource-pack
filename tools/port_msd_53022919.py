#!/usr/bin/env python3
"""Guarded port of Mega Showdown 18dfa756..53022919 model/texture updates.

Species with custom skins/forms receive isolated ``atlas_msd18_*`` model/poser/animation
sets and ``textures/pokemon/atlas_msd18/`` textures as extra guarded resolver variations.
Legacy rigs, textures and skin variations are never rewritten. MSD ``mega_z``/``mega_x``/
``mega_y`` aspects are translated to this pack's ``mega-z``/``mega-x``/``mega-y`` flags.
"""
from pathlib import Path
import json, subprocess, copy, hashlib, re, shutil

ROOT = Path(__file__).resolve().parents[1]
UP = ROOT.parent / 'CobblemonMegaShowdown'
CORE = ROOT.parent / 'cobblemon/common/src/main/resources/assets/cobblemon'
HEAD = '53022919'; PREVIOUS = '18dfa756'
UPFX = 'common/src/main/resources/assets/cobblemon/'
REPORT = ROOT / 'reports/mega-showdown-1.8-53022919-port.json'
BEFORE = ROOT / 'reports/mega-showdown-1.8-53022919-before'
A = ROOT / 'assets/cobblemon/bedrock/pokemon'
TEX = ROOT / 'assets/cobblemon/textures/pokemon'
STANDARD = ['shiny', 'male', 'female', 'alpha_eyes', 'cosmetic_item-black_glasses', 'cosmetic_item-wise_glasses']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def up_bytes(path):
    return subprocess.check_output(['git', 'show', f'{HEAD}:{UPFX}{path}'], cwd=UP)
def up_json(path): return json.loads(up_bytes(path))
def T(rel): return 'cobblemon:textures/pokemon/atlas_msd18/' + rel
def alias(name): return 'atlas_msd18_' + name

files = {}      # relative pack path -> {sha256, upstream}
backups = {}    # relative pack path -> sha256 before edit
legacy_resolvers = {}

def backup(path: Path):
    rel = str(path.relative_to(ROOT))
    if rel in backups or not path.exists(): return
    backups[rel] = sha(path)
    dest = BEFORE / rel; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(path.read_bytes())

def write(path: Path, data: bytes, upstream: str):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    files[str(path.relative_to(ROOT))] = {'sha256': sha(path), 'upstream': upstream}

def rename_groups(text: str, groups):
    for g in groups:
        text = re.sub(r"(bedrock\w*\(\s*')" + re.escape(g) + r"(')", lambda m: m.group(1) + alias(g) + m.group(2), text)
    return text

def import_animation(group, source_json, upstream_label):
    """Copy an animation file, renaming its group to atlas_msd18_<group>."""
    out = {}
    for k, v in source_json['animations'].items():
        assert k.startswith('animation.' + group + '.'), (group, k)
        out['animation.' + alias(group) + k[len('animation.' + group):]] = v
    doc = dict(source_json); doc['animations'] = out
    write(A / 'animations/atlas_msd18' / (alias(group) + '.animation.json'), (json.dumps(doc, indent=2) + '\n').encode(), upstream_label)

def import_set(name, updir, groups, textures, texdir, poser_src=None, anim_sources=None):
    """Model + poser + animation groups + textures into isolated atlas_msd18 IDs."""
    geo = up_json(f'bedrock/pokemon/models/{updir}/{name}.geo.json')
    write(A / 'models/atlas_msd18' / (alias(name) + '.geo.json'), (json.dumps(geo, indent=2) + '\n').encode(), f'bedrock/pokemon/models/{updir}/{name}.geo.json')
    poser_src = poser_src or f'bedrock/pokemon/posers/{updir}/{name}.json'
    text = up_bytes(poser_src).decode()
    found = set(re.findall(r"bedrock\w*\(\s*'(\w+)'", text))
    assert found == set(groups), (name, found, groups)
    poser = json.loads(rename_groups(text, groups))
    root = poser.get('rootBone')
    if root: assert any(b['name'] == root for b in geo['minecraft:geometry'][0]['bones']), (name, root)
    write(A / 'posers/atlas_msd18' / (alias(name) + '.json'), (json.dumps(poser, indent=2) + '\n').encode(), poser_src)
    for group, source in (anim_sources or {}).items():
        if source == 'core':
            src = CORE / f'bedrock/pokemon/animations/{updir}/{group}.animation.json'
            import_animation(group, json.loads(src.read_text()), str(src))
        else:
            import_animation(group, up_json(source), source)
    for tex in textures:
        write(TEX / 'atlas_msd18' / texdir / tex, up_bytes(f'textures/pokemon/{updir}/{tex}'), f'textures/pokemon/{updir}/{tex}')

def load_resolver(path: Path):
    return json.loads(path.read_text()) if path.exists() else None

def species_aspects(species):
    return {a for p in (A / 'resolvers').rglob('*.json') for v in json.loads(p.read_text())['variations']
            for a in v.get('aspects', []) if json.loads(p.read_text()).get('species', json.loads(p.read_text()).get('name')) == species}

updates = []; guards = []

def add_variations(species, form, resolver_rel, variations, source, order=None, managed=None):
    path = ROOT / resolver_rel
    doc = load_resolver(path)
    if doc is None:
        doc = {'species': species, 'order': order, 'variations': []}
        legacy_resolvers[resolver_rel] = {'species': species, 'order': order, 'variations': []}
    else:
        legacy_resolvers[resolver_rel] = copy.deepcopy(doc)
    allowed = set(STANDARD) | set(form)
    blocked = sorted(a for a in species_aspects(species) if a not in allowed)
    guard = ' && '.join("!q.has_aspect('" + a + "')" for a in blocked)
    new = []
    for v in variations:
        v = copy.deepcopy(v)
        if guard and 'atlas_msd18' in json.dumps(v): v['condition'] = guard
        new.append(v)
    doc['variations'] = doc['variations'] + new
    write(path, (json.dumps(doc, indent=2) + '\n').encode(), source)
    updates.append({'species': species, 'form': form, 'resolver': resolver_rel, 'source': source,
                    'protected_aspects': blocked, 'new_variations': new})
    guards.append({'species': species, 'form': form, 'resolver': resolver_rel, 'standard_aspects': STANDARD,
                   'managed_aspect_sets': managed or [v['aspects'] for v in variations]})

def main():
    assert not REPORT.exists(), 'Port already recorded; validate instead of replacing before snapshots'
    assert subprocess.check_output(['git', 'rev-parse', '--short=8', 'HEAD'], cwd=UP, text=True).strip() == HEAD
    before = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'assets').rglob('*') if p.is_file()}
    RES = 'assets/cobblemon/bedrock/pokemon/resolvers/'
    UPRES = 'bedrock/pokemon/resolvers/'

    # 1. Mega Absol remodel + new Mega Absol Z (legacy absol_mega/absol_mega_z rigs and posers carry skins).
    import_set('absol_mega', '0359_absol', ['absol_mega'], ['absol_mega.png', 'absol_mega_shiny.png'], '0359_absol',
               anim_sources={'absol_mega': 'bedrock/pokemon/animations/0359_absol/absol_mega.animation.json'})
    add_variations('cobblemon:absol', ['mega'], RES + 'pokemon/megas/0359_absol/1_absol_mega.json', [
        {'aspects': ['mega'], 'poser': 'cobblemon:' + alias('absol_mega'), 'model': 'cobblemon:' + alias('absol_mega') + '.geo', 'texture': T('0359_absol/absol_mega.png'), 'layers': []},
        {'aspects': ['mega', 'shiny'], 'texture': T('0359_absol/absol_mega_shiny.png')}], UPRES + '0359_absol/1_absol_mega.json')
    import_set('absol_mega_z', '0359_absol', ['absol_mega_z'], ['absol_mega_z.png', 'absol_mega_z_shiny.png'], '0359_absol',
               anim_sources={'absol_mega_z': 'bedrock/pokemon/animations/0359_absol/absol_mega_z.animation.json'})
    add_variations('cobblemon:absol', ['mega-z'], RES + 'pokemon/megas/0359_absol/3_absol_mega_z.json', [
        {'aspects': ['mega-z'], 'poser': 'cobblemon:' + alias('absol_mega_z'), 'model': 'cobblemon:' + alias('absol_mega_z') + '.geo', 'texture': T('0359_absol/absol_mega_z.png'), 'layers': [{'name': 'glow', 'enabled': False}]},
        {'aspects': ['mega-z', 'shiny'], 'texture': T('0359_absol/absol_mega_z_shiny.png')}], UPRES + '0359_absol/2_absol_mega_z.json')

    # 2. Lucario VGU: base (core animation group + upstream mega group), mega (emissive/alpha, core lucario_aura particle), mega Z.
    import_set('lucario', '0448_lucario', ['lucario', 'lucario_mega'], ['lucario.png', 'lucario_shiny.png', 'lucario_alpha.png'], '0448_lucario',
               anim_sources={'lucario': 'core'})
    import_set('lucario_mega', '0448_lucario', ['lucario_mega'], ['lucario_mega.png', 'lucario_mega_shiny.png', 'lucario_mega_alpha.png', 'lucario_mega_emissive.png'], '0448_lucario',
               anim_sources={'lucario_mega': 'bedrock/pokemon/animations/0448_lucario/lucario_mega.animation.json'})
    import_set('lucario_mega_z', '0448_lucario', ['dummy', 'lucario_mega_z'], ['lucario_mega_z.png', 'lucario_mega_z_shiny.png'], '0448_lucario',
               anim_sources={'lucario_mega_z': 'bedrock/pokemon/animations/0448_lucario/lucario_mega_z.animation.json'})
    add_variations('cobblemon:lucario', [], RES + 'atlas_msd18/120_lucario.json', [
        {'aspects': [], 'poser': 'cobblemon:' + alias('lucario'), 'model': 'cobblemon:' + alias('lucario') + '.geo', 'texture': T('0448_lucario/lucario.png'),
         'layers': [{'name': 'alpha_eyes', 'enabled': False}, {'name': 'aura', 'enabled': False}, {'name': 'emissive', 'enabled': False}]},
        {'aspects': ['shiny'], 'texture': T('0448_lucario/lucario_shiny.png')},
        {'aspects': ['alpha_eyes'], 'layers': [{'name': 'alpha_eyes', 'texture': T('0448_lucario/lucario_alpha.png'), 'emissive': True}]}],
        str(CORE / 'bedrock/pokemon/resolvers/0448_lucario/0_lucario_base.json'), order=120)
    add_variations('cobblemon:lucario', ['mega'], RES + 'pokemon/megas/0448_lucario/1_lucario_mega.json', [
        {'aspects': ['mega'], 'poser': 'cobblemon:' + alias('lucario_mega'), 'model': 'cobblemon:' + alias('lucario_mega') + '.geo', 'texture': T('0448_lucario/lucario_mega.png'),
         'layers': [{'name': 'emissive', 'texture': T('0448_lucario/lucario_mega_emissive.png'), 'emissive': True, 'translucent': True}]},
        {'aspects': ['mega', 'shiny'], 'texture': T('0448_lucario/lucario_mega_shiny.png')},
        {'aspects': ['mega', 'alpha_eyes'], 'layers': [{'name': 'alpha_eyes', 'texture': T('0448_lucario/lucario_mega_alpha.png'), 'emissive': False}]}],
        UPRES + '0448_lucario/1_lucario_mega.json')
    add_variations('cobblemon:lucario', ['mega-z'], RES + 'pokemon/megas/0448_lucario/3_lucario_mega_z.json', [
        {'aspects': ['mega-z'], 'poser': 'cobblemon:' + alias('lucario_mega_z'), 'model': 'cobblemon:' + alias('lucario_mega_z') + '.geo', 'texture': T('0448_lucario/lucario_mega_z.png'), 'layers': []},
        {'aspects': ['mega-z', 'shiny'], 'texture': T('0448_lucario/lucario_mega_z_shiny.png')}], UPRES + '0448_lucario/2_lucario_mega_z.json')

    # 4. Mega Golisopod (anniversary skins keep the legacy rig/poser).
    import_set('golisopod_mega', '0768_golisopod', ['dummy', 'golisopod_mega'], ['golisopod_mega.png', 'golisopod_mega_shiny.png', 'golisopod_mega_alpha.png'], '0768_golisopod',
               anim_sources={'golisopod_mega': 'bedrock/pokemon/animations/0768_golisopod/golisopod_mega.animation.json'})
    add_variations('cobblemon:golisopod', ['mega'], RES + 'pokemon/megas/0768_golisopod/7_golisopod_mega.json', [
        {'aspects': ['mega'], 'poser': 'cobblemon:' + alias('golisopod_mega'), 'model': 'cobblemon:' + alias('golisopod_mega') + '.geo', 'texture': T('0768_golisopod/golisopod_mega.png'), 'layers': []},
        {'aspects': ['mega', 'shiny'], 'texture': T('0768_golisopod/golisopod_mega_shiny.png')},
        {'aspects': ['mega', 'alpha_eyes'], 'layers': [{'name': 'alpha_eyes', 'texture': T('0768_golisopod/golisopod_mega_alpha.png'), 'emissive': True}]}],
        UPRES + '0768_golisopod/1_golisopod_mega.json')

    # 5. Frigibax line base remodels + Mega Baxcalibur (legacy community rigs carry medieval skin / duplicate mega resolvers).
    for name, updir, resolver in [('frigibax', '0996_frigibax', 'pokemon/09_generation/frigibax.json'), ('arctibax', '0997_arctibax', 'pokemon/09_generation/arctibax.json'), ('baxcalibur', '0998_baxcalibur', 'pokemon/09_generation/baxcalibur.json')]:
        import_set(name, updir, [name], [name + '.png', name + '_shiny.png', name + '_alpha.png'], updir,
                   anim_sources={name: f'bedrock/pokemon/animations/{updir}/{name}.animation.json'})
        add_variations('cobblemon:' + name, [], RES + resolver, [
            {'aspects': [], 'poser': 'cobblemon:' + alias(name), 'model': 'cobblemon:' + alias(name) + '.geo', 'texture': T(f'{updir}/{name}.png'), 'layers': []},
            {'aspects': ['shiny'], 'texture': T(f'{updir}/{name}_shiny.png'), 'layers': []},
            {'aspects': ['alpha_eyes'], 'layers': [{'name': 'alpha_eyes', 'texture': T(f'{updir}/{name}_alpha.png'), 'emissive': True}]}],
            UPRES + f'{updir}/0_{name}_base.json')
    import_set('baxcalibur_mega', '0998_baxcalibur', ['baxcalibur_mega'], ['baxcalibur_mega.png', 'baxcalibur_mega_shiny.png'], '0998_baxcalibur',
               anim_sources={'baxcalibur_mega': 'bedrock/pokemon/animations/0998_baxcalibur/baxcalibur_mega.animation.json'})
    add_variations('cobblemon:baxcalibur', ['mega'], RES + 'atlas_msd18/100_baxcalibur_mega.json', [
        {'aspects': ['mega'], 'poser': 'cobblemon:' + alias('baxcalibur_mega'), 'model': 'cobblemon:' + alias('baxcalibur_mega') + '.geo', 'texture': T('0998_baxcalibur/baxcalibur_mega.png'), 'layers': []},
        {'aspects': ['mega', 'shiny'], 'texture': T('0998_baxcalibur/baxcalibur_mega_shiny.png'), 'layers': []}],
        UPRES + '0998_baxcalibur/1_baxcalibur_mega.json', order=100)

    # 6. Chi-Yu base remodel with emissive layers (st-patricks skins keep the legacy rig/poser).
    import_set('chiyu', '1004_chiyu', ['chiyu'], ['chiyu.png', 'chiyu_shiny.png', 'chiyu_emissive.png', 'chiyu_shiny_emissive.png'], '1004_chiyu',
               anim_sources={'chiyu': 'bedrock/pokemon/animations/1004_chiyu/chiyu.animation.json'})
    add_variations('cobblemon:chiyu', [], RES + 'pokemon/09_generation/chiyu.json', [
        {'aspects': [], 'poser': 'cobblemon:' + alias('chiyu'), 'model': 'cobblemon:' + alias('chiyu') + '.geo', 'texture': T('1004_chiyu/chiyu.png'),
         'layers': [{'name': 'emissive', 'emissive': True, 'texture': T('1004_chiyu/chiyu_emissive.png')}]},
        {'aspects': ['shiny'], 'texture': T('1004_chiyu/chiyu_shiny.png'), 'layers': [{'name': 'emissive', 'emissive': True, 'texture': T('1004_chiyu/chiyu_shiny_emissive.png')}]}],
        UPRES + '1004_chiyu/0_chiyu_base.json')

    # 8. Mega Delphox alias: upstream added ride seat locators and widened visible bounds; artwork/UVs unchanged.
    target = A / 'models/atlas_msd18/atlas_msd18_delphoxmega.geo.json'
    local = json.loads(target.read_text()); new = up_json('bedrock/pokemon/models/0655_delphox/delphoxmega.geo.json')
    lg, ng = local['minecraft:geometry'][0], new['minecraft:geometry'][0]
    lb = {b['name'] for b in lg['bones']}
    added = [copy.deepcopy(b) for b in ng['bones'] if b['name'] not in lb]
    assert [b['name'] for b in added] == ['locator_seat_2', 'locator_seat_1'] and all(not b.get('cubes') and b.get('locators') and b.get('parent') in lb for b in added)
    lg['bones'] += added; lg['description']['visible_bounds_width'] = ng['description']['visible_bounds_width']
    write(target, (json.dumps(local, indent=2) + '\n').encode(), 'bedrock/pokemon/models/0655_delphox/delphoxmega.geo.json')
    delphox = {'added_bones': [b['name'] for b in added], 'visible_bounds_width': ng['description']['visible_bounds_width']}

    # 9. Stock-blob alias/mega texture replacements whose local geometry has identical cube UVs to upstream HEAD.
    stock = {
        'assets/cobblemon/textures/pokemon/atlas_msd18/0655_delphox/delphox_mega_shiny.png': 'textures/pokemon/0655_delphox/delphox_mega_shiny.png',
        'assets/cobblemon/textures/pokemon/atlas_msd18/0638_cobalion/cobalion.png': 'textures/pokemon/0638_cobalion/cobalion.png',
        'assets/cobblemon/textures/pokemon/atlas_msd18/0638_cobalion/cobalion_shiny.png': 'textures/pokemon/0638_cobalion/cobalion_shiny.png',
        'assets/cobblemon/textures/pokemon/atlas_msd18/1014_okidogi/okidogi.png': 'textures/pokemon/1014_okidogi/okidogi.png',
        'assets/cobblemon/textures/pokemon/atlas_msd18/1014_okidogi/okidogi_shiny.png': 'textures/pokemon/1014_okidogi/okidogi_shiny.png',
        'assets/cobblemon/textures/pokemon/megas/0006_charizard/charizard_mega_y_shiny.png': 'textures/pokemon/0006_charizard/charizard_mega_y_shiny.png',
        'assets/cobblemon/textures/pokemon/megas/0006_charizard/charizard_mega_x_shiny.png': 'textures/pokemon/0006_charizard/megacharizardx_shiny.png',
    }
    blobs = set(subprocess.check_output(['git', 'cat-file', '--batch-all-objects', '--batch-check'], cwd=UP, text=True).split('\n'))
    blobs = {line.split()[0] for line in blobs if ' blob ' in line}
    for rel, source in stock.items():
        path = ROOT / rel
        assert subprocess.check_output(['git', 'hash-object', str(path)], text=True).strip() in blobs, ('not a stock MSD blob', rel)
        write(path, up_bytes(source), source)

    (ROOT / 'tools/msd18-skin-guards.json').write_text(json.dumps(json.loads((ROOT / 'tools/msd18-skin-guards.json').read_text()) + guards, indent=2) + '\n')
    result = {'upstream': HEAD, 'previous_upstream': PREVIOUS, 'updates': updates, 'files': files, 'legacy_resolvers': legacy_resolvers,
              'before_asset_hashes': before, 'backups': backups, 'stock_texture_replacements': sorted(stock), 'delphox_alias': delphox,
              'baseline_sha256': sha(ROOT / 'client-baseline.json')}
    REPORT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'updates': len(updates), 'files': len(files), 'edited_existing': len(backups), 'guards_added': len(guards)}))

if __name__ == '__main__': main()
