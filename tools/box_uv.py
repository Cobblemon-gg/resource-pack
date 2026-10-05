"""Reatlas per-face Bedrock UVs for Cobblemon's box-UV-only TexturedModel.

PNG pixels are denser than logical texture units, preserving detailed faces on
fractional-sized cubes without changing geometry, pivots, or animation bones.
"""
import copy
import math
from PIL import Image


def face_rects(size, offset):
    x, y, z = size
    u, v = offset
    return {
        'east': (u, v + z, z, y),
        'north': (u + z, v + z, x, y),
        'west': (u + z + x, v + z, z, y),
        'south': (u + 2*z + x, v + z, x, y),
        # Bedrock per-face export reverses both axes of Blockbench's cap UVs.
        'up': (u + z, v, x, z),
        'down': (u + z + x, v + z, x, -z),
    }


def convert(model, texture, density=8):
    result = copy.deepcopy(model)
    assert len(result['minecraft:geometry']) == 1
    geometry = result['minecraft:geometry'][0]
    desc = geometry['description']
    source = texture.convert('RGBA')
    sx = source.width / desc['texture_width']
    sy = source.height / desc['texture_height']
    cubes = [c for b in geometry['bones'] for c in b.get('cubes', [])]
    assert all(isinstance(c['uv'], dict) and not c.get('mirror') for c in cubes)
    sizes = [(math.ceil(2*(c['size'][0]+c['size'][2]))+2,
              math.ceil(c['size'][1]+c['size'][2])+2) for c in cubes]
    width = 2 ** math.ceil(math.log2(max(max(w for w,h in sizes),
                                      math.sqrt(sum(w*h for w,h in sizes)))))
    x, y, row = 0, 0, 0
    offsets = []
    for w, h in sizes:
        if x+w > width:
            x, y, row = 0, y+row, 0
        offsets.append((x+1, y+1))
        x += w
        row = max(row, h)
    height = 2 ** math.ceil(math.log2(y+row))
    atlas = Image.new('RGBA', (width*density, height*density))
    pixels, original = atlas.load(), source.load()
    for cube, offset in zip(cubes, offsets):
        for face, (u, v, w, h) in face_rects(cube['size'], offset).items():
            if not w or not h or face not in cube['uv']:
                continue
            spec = cube['uv'][face]
            assert not spec.get('uv_rotation'), 'Rotated UVs need explicit conversion'
            a, b = spec['uv']
            dw, dh = spec['uv_size']
            for py in range(math.ceil(min(v, v+h)*density-.5), math.ceil(max(v, v+h)*density-.5)):
                for px in range(math.ceil(min(u, u+w)*density-.5), math.ceil(max(u, u+w)*density-.5)):
                    tx = math.floor((a + ((px+.5)/density-u)/w*dw)*sx)
                    ty = math.floor((b + ((py+.5)/density-v)/h*dh)*sy)
                    assert 0 <= tx < source.width and 0 <= ty < source.height
                    pixels[px, py] = original[tx, ty]
        cube['uv'] = list(offset)
    desc['texture_width'], desc['texture_height'] = width, height
    return result, atlas
