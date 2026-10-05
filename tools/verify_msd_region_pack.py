"""Check MSD region-pack dependencies with Atlas's MSD asset filter applied.

This is a focused static dependency check, not a whole-client rendering audit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

from audit_installed_models import merge, model_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--overlay', type=Path, required=True)
    parser.add_argument('--baseline-below-mods', action='store_true')
    args = parser.parse_args()
    resources, mods = {}, {}
    for jar in sorted((args.profile / 'mods').glob('*.jar')):
        with zipfile.ZipFile(jar) as archive:
            if 'fabric.mod.json' not in archive.namelist():
                continue
            mod_id = json.loads(archive.read('fabric.mod.json'), strict=False)['id']
        mods[mod_id] = jar
        layer = {}
        merge(layer, jar)
        if mod_id == 'mega_showdown':
            for name in list(layer):
                if name.startswith(('assets/cobblemon/bedrock/pokemon/', 'assets/cobblemon/textures/pokemon/')):
                    gmax = any(marker in name for marker in ('gmax', 'gigantamax'))
                    owned = any(species in name for species in ('0842_appletun', '0569_garbodor', '0841_flapple'))
                    if not gmax or owned:
                        del layer[name]
        resources.update(layer)
    if args.baseline_below_mods:
        baseline = {}
        merge(baseline, mods['atlas-client'], 'resourcepacks/atlas_baseline/')
        baseline.update(resources)
        resources = baseline
    else:
        merge(resources, mods['atlas-client'], 'resourcepacks/atlas_baseline/')
    merge(resources, mods['cobblemon'], 'resourcepacks/regionbiasforms/')
    region = {}
    merge(region, mods['mega_showdown'], 'resourcepacks/regionbiasmsd/')
    resources.update(region)
    merge(resources, args.overlay)

    manifest = json.loads((Path(__file__).resolve().parents[1] / 'reports/msd-region-pikachu-20261005.json').read_text())
    with zipfile.ZipFile(args.overlay) as archive:
        for name, digest in manifest['assets'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name

    indexes = {}
    for kind in ('models', 'posers', 'animations'):
        indexes[kind] = {
            name.split('/')[1] + ':' + Path(name).name.removesuffix('.json'): name
            for name in resources if '/bedrock/pokemon/' + kind + '/' in name and name.endswith('.json')
        }
    checked = 0
    posers = set()
    def check(value):
        nonlocal checked
        if isinstance(value, list):
            for child in value:
                check(child)
        elif isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, str) and key in ('model', 'poser', 'texture'):
                    if key == 'texture':
                        namespace, path = child.split(':', 1)
                        assert 'assets/' + namespace + '/' + path in resources, child
                    else:
                        assert child in indexes[key + 's'], child
                        if key == 'poser':
                            posers.add(child)
                    checked += 1
                else:
                    check(child)
    for name, (data, _) in region.items():
        if '/resolvers/' in name and name.endswith('.json'):
            check(model_json(data))
    animation_count = 0
    for poser in posers:
        data = model_json(resources[indexes['posers'][poser]][0])
        for group, animation in re.findall(r"q\.bedrock(?:_stateful|_quirk)?\('([^']+)',\s*'([^']+)'", json.dumps(data)):
            name = indexes['animations'].get('cobblemon:' + group + '.animation')
            assert name, group
            animations = model_json(resources[name][0])['animations']
            assert 'animation.' + group + '.' + animation in animations, (group, animation)
            animation_count += 1
    print(f'PASS: {len(manifest["assets"])} exact upstream assets in overlay; '
          f'{checked} region model/poser/texture references and {animation_count} animation calls resolve with MSD filtering.')


if __name__ == '__main__':
    main()
