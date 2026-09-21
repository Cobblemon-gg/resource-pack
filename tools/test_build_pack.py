"""Exercise server updates against a frozen client, including removed resolver masking."""
import argparse, contextlib, io, json, tempfile, unittest, zipfile
from pathlib import Path
from build_pack import build, freeze, annotate_upstream

class PackSplitTest(unittest.TestCase):
    def test_unchanged_server_override_wins_over_mod_between_baseline_and_overlay(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'pack'; client=Path(temp)/'client'; upstream=Path(temp)/'upstream'
            asset='assets/cobblemon/bedrock/pokemon/resolvers/0384_rayquaza/0_rayquaza_base.json'
            custom=b'{"species":"cobblemon:rayquaza","variations":[{"aspects":["skel"]}]}'
            normal=b'{"species":"cobblemon:rayquaza","variations":[{"aspects":[]}]}'
            for folder,data in ((root,custom),(upstream,normal)):
                target=folder/asset;target.parent.mkdir(parents=True);target.write_bytes(data)
            args=argparse.Namespace(root=root,client=client,manifest=root/'client-baseline.json',output=root/'dist',baseline_id='test',replace_baseline=False,upstream_source=[upstream])
            with contextlib.redirect_stdout(io.StringIO()):freeze(args)
            archive=client/'resource-pack/atlas-baseline.zip'; frozen=archive.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):build(args)
            with zipfile.ZipFile(args.output/'resource-pack.zip') as z:
                self.assertNotIn(asset,z.namelist())
            (root/'server-overrides.json').write_text(json.dumps({asset:'Repair baseline priority'}))
            with contextlib.redirect_stdout(io.StringIO()):build(args)
            with zipfile.ZipFile(archive) as z:effective={asset:z.read(asset)}
            effective[asset]=normal  # Mod assets override a misplaced baseline.
            with zipfile.ZipFile(args.output/'resource-pack.zip') as z:
                effective.update({n:z.read(n) for n in z.namelist()})
            self.assertEqual(effective[asset],custom)
            self.assertEqual(archive.read_bytes(),frozen)
            # A typo/deleted pin must never silently drop the repair.
            (root/'server-overrides.json').write_text(json.dumps({asset+'.missing':'Typo'}))
            with self.assertRaisesRegex(SystemExit,'Server override assets are missing'):
                build(args)

    def test_overlay_reconstructs_changed_new_deleted_assets_without_new_client(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'pack'; client=Path(temp)/'client'; (root/'assets/cobblemon').mkdir(parents=True)
            (root/'assets/cobblemon/skin.png').write_bytes(b'original skin')
            (root/'assets/cobblemon/resolver.json').write_text('{"species":"cobblemon:absol","variations":[]}')
            (root/'assets/cobblemon/model.bbmodel').write_text('authoring only')
            upstream=Path(temp)/'upstream'; (upstream/'assets').mkdir(parents=True)
            args=argparse.Namespace(upstream_source=[upstream],root=root,client=client,manifest=root/'client-baseline.json',output=root/'dist',baseline_id='test',replace_baseline=False)
            with contextlib.redirect_stdout(io.StringIO()): freeze(args)
            archive=client/'resource-pack/atlas-baseline.zip'; frozen=archive.read_bytes()
            (root/'assets/cobblemon/skin.png').write_bytes(b'new skin')
            (root/'assets/cobblemon/tag.png').write_bytes(b'new tag')
            (root/'assets/cobblemon/resolver.json').unlink()
            with contextlib.redirect_stdout(io.StringIO()): build(args)
            self.assertEqual(frozen, archive.read_bytes())
            with zipfile.ZipFile(args.output/'resource-pack.zip') as z:
                self.assertEqual(set(z.namelist()),{'pack.mcmeta','assets/cobblemon/skin.png','assets/cobblemon/tag.png'})
                self.assertEqual(z.read('assets/cobblemon/skin.png'),b'new skin')
                self.assertEqual(json.loads(z.read('pack.mcmeta'))['filter']['block'],[{'namespace':'cobblemon','path':r'resolver\.json'}])
            # Metadata/ZIP timestamp determinism keeps pack SHA1 stable on unchanged rebuilds.
            first=(args.output/'resource-pack.zip').read_bytes()
            with contextlib.redirect_stdout(io.StringIO()): build(args)
            self.assertEqual(first,(args.output/'resource-pack.zip').read_bytes())

    def test_upstream_override_deletion_is_rejected_until_fallback_is_supplied(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'pack';client=Path(temp)/'client';upstream=Path(temp)/'upstream'
            for path in ('assets/cobblemon/bedrock/pokemon/models/base.geo.json', 'assets/minecraft/font/default.json'):
                for folder,content in ((upstream,b'upstream fallback'),(root,b'custom override')):
                    p=folder/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
            custom='assets/minecraft/font/atlas_tags.json'
            (root/custom).write_bytes(b'custom font')
            args=argparse.Namespace(root=root,client=client,manifest=root/'client-baseline.json',output=root/'dist',baseline_id='test',replace_baseline=False,upstream_source=[upstream])
            with contextlib.redirect_stdout(io.StringIO()):freeze(args)
            archive=client/'resource-pack/atlas-baseline.zip';frozen=archive.read_bytes()
            client_metadata=archive.with_name('baseline.json').read_bytes()
            # Metadata-only upgrades never change the already distributed client snapshot.
            with contextlib.redirect_stdout(io.StringIO()):annotate_upstream(args)
            self.assertEqual(frozen,archive.read_bytes())
            self.assertEqual(client_metadata,archive.with_name('baseline.json').read_bytes())
            for path in ('assets/cobblemon/bedrock/pokemon/models/base.geo.json', 'assets/minecraft/font/default.json'):
                (root/path).unlink()
                with self.assertRaisesRegex(SystemExit,'Copy the desired upstream fallback bytes'):
                    build(args)
                self.assertFalse((args.output/'resource-pack.zip').exists())
                (root/path).write_bytes((upstream/path).read_bytes())
            (root/custom).unlink()
            with contextlib.redirect_stdout(io.StringIO()):build(args)
            with zipfile.ZipFile(args.output/'resource-pack.zip') as z:
                blocks=json.loads(z.read('pack.mcmeta'))['filter']['block']
                self.assertEqual(blocks,[{'namespace':'minecraft','path':r'font/atlas_tags\.json'}])
                self.assertEqual(z.read('assets/cobblemon/bedrock/pokemon/models/base.geo.json'),b'upstream fallback')
                self.assertEqual(z.read('assets/minecraft/font/default.json'),b'upstream fallback')
            self.assertEqual(frozen,archive.read_bytes())

if __name__=='__main__': unittest.main()
