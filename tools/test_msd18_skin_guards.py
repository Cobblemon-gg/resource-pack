import json,tempfile,unittest
from pathlib import Path
from msd18_skin_guards import check

class LegacySkinGuards(unittest.TestCase):
    def test_new_skin_fails_until_guard_is_refreshed_without_changing_skin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'assets/cobblemon/bedrock/pokemon/resolvers';folder.mkdir(parents=True)
            (root/'tools').mkdir();p=folder/'test.json'
            old={'model':'cobblemon:test.geo'}
            new={'model':'cobblemon:atlas_msd18_test.geo'}
            skin={'aspects':['new-skin'], 'model':'cobblemon:atlas_msd18_test.geo', 'texture':'cobblemon:textures/new.png'}
            p.write_text(json.dumps({'species':'cobblemon:test','variations':[old,new,skin]}))
            (root/'tools/msd18-skin-guards.json').write_text(json.dumps([{'species':'cobblemon:test','resolver':str(p.relative_to(root)),'standard_aspects':['shiny'],'form':[],'managed_aspect_sets':[[]]}]))
            with self.assertRaises(SystemExit):check(root)
            check(root,refresh=True);check(root)
            variants=json.loads(p.read_text())['variations']
            self.assertEqual(variants[0],old);self.assertEqual(variants[2],skin)
            self.assertEqual(variants[1]['condition'],"!q.has_aspect('new-skin')")
            before=p.read_bytes();check(root,refresh=True);self.assertEqual(p.read_bytes(),before)

    def test_generic_build_fixture_without_msd_assets_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:check(Path(tmp))

if __name__=='__main__':unittest.main()
