"""Reject per-face UV objects unsupported by the distributed client loader."""
import json


def check(files):
    errors = []
    count = 0
    for path, data in files.items():
        if not path.endswith('.json') or not any(part in path for part in
                ('/models/bedrock/models/', '/bedrock/pokemon/models/')):
            continue
        # Some legacy placeholder resources are not geometry documents.
        if not data.lstrip().startswith(b'{'):
            continue
        model = json.loads(data)
        for geometry in model.get('minecraft:geometry', []):
            for bone in geometry.get('bones', []):
                for cube in bone.get('cubes', []):
                    count += 1
                    uv = cube.get('uv')
                    if uv is not None and (not isinstance(uv, list) or len(uv) != 2
                            or any(type(n) not in (int, float) or n != int(n) for n in uv)):
                        errors.append(f'{path}: bone {bone["name"]}: uv must be two integers')
    if errors:
        raise SystemExit('Unsupported Bedrock UV data:\n' + '\n'.join(errors))
    return count
