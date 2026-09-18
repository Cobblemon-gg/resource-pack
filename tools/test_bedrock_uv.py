import json
import unittest
from check_bedrock_uv import check


class BedrockUvTest(unittest.TestCase):
    def model(self, uv):
        return json.dumps({'minecraft:geometry': [{'bones': [
            {'name': 'root', 'cubes': [{'uv': uv}]}]}]}).encode()

    def test_both_loaders_reject_per_face_uv(self):
        for path in ('assets/minecraft/models/bedrock/models/wing.json',
                     'assets/cobblemon/bedrock/pokemon/models/plushie.geo.json'):
            with self.assertRaisesRegex(SystemExit, 'uv must be two integers'):
                check({path: self.model({'north': {'uv': [0, 0]}})})

    def test_box_uv_and_fractional_geometry_allowed(self):
        self.assertEqual(check({'assets/minecraft/models/bedrock/models/a.json':
                                self.model([1, 2])}), 1)

    def test_item_face_uvs_are_not_bedrock(self):
        self.assertEqual(check({'assets/minecraft/models/item/a.json':
                                self.model({'north': {}})}), 0)

    def test_fractional_offsets_rejected(self):
        with self.assertRaises(SystemExit):
            check({'assets/minecraft/models/bedrock/models/a.json': self.model([0.5, 2])})


if __name__ == '__main__':
    unittest.main()
