import copy
import unittest
from PIL import Image
from box_uv import convert


class BoxConversionTest(unittest.TestCase):
    def test_six_asymmetric_faces_and_geometry(self):
        source = Image.new('RGBA', (24, 24))
        for x in range(24):
            for y in range(24):
                source.putpixel((x, y), (x*10, y*10, 50, 255))
        specs = {face: {'uv': [2, 3], 'uv_size': [4, 6]}
                 for face in ('north', 'south', 'east', 'west', 'up', 'down')}
        cube = {'size': [4, 6, 3], 'origin': [1, 2, 3], 'pivot': [3, 4, 5],
                'rotation': [0, 0, 25], 'uv': specs}
        model = {'minecraft:geometry': [{'description': {'texture_width': 24, 'texture_height': 24},
                 'bones': [{'name': 'root', 'pivot': [0, 0, 0], 'cubes': [cube]}]}]}
        before = copy.deepcopy(model)
        result, image = convert(model, source)
        self.assertEqual(model, before)
        new = result['minecraft:geometry'][0]['bones'][0]['cubes'][0]
        self.assertEqual({k:v for k,v in cube.items() if k != 'uv'},
                         {k:v for k,v in new.items() if k != 'uv'})
        u, v = new['uv']
        # Independent Bedrock box-net positions, including reversed bottom V.
        faces = [(u+3,v+3,4,6), (u+10,v+3,4,6), (u,v+3,3,6),
                 (u+7,v+3,3,6), (u+3,v,4,3), (u+7,v+3,4,-3)]
        for a,b,w,h in faces:
            for x,y in ((.125,.125),(.375,.375),(.625,.625),(.875,.875)):
                self.assertEqual(image.getpixel((int((a+w*x)*8),int((b+h*y)*8))),
                                 source.getpixel((int(2+4*x),int(3+6*y))))


if __name__ == '__main__':
    unittest.main()
