import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from cre_import import append_bone, add_property, geometry, run, seat_for, seat_reference


def model(root='root', body='body', pivot=None, seat=False):
    bones = [{'name': root, 'pivot': [0, 0, 0]}, {'name': body, 'parent': root, 'pivot': pivot or [0, 5, 0], 'cubes': [{'uv': [1, 2], 'size': [2, 3, 4]}]}]
    if seat:
        bones.append({'name': 'locator_seat_1', 'parent': body, 'pivot': [0, 10, 1], 'locators': {'seat_1': [0, 10, 1]}})
    return {'format_version': '1.12.0', 'minecraft:geometry': [{'description': {'texture_width': 64, 'texture_height': 32}, 'bones': bones}]}


class CreImportTest(unittest.TestCase):
    def test_seat_translates_relative_to_parent_without_geometry_edits(self):
        reference = seat_reference(model(seat=True))
        target = model(pivot=[2, 9, 0])
        before = copy.deepcopy(target)
        bone, rule = seat_for(target, reference)
        self.assertEqual('A', rule)
        self.assertEqual([2, 14, 1], bone['locators']['seat_1'])
        self.assertEqual(before, target)

    def test_fallback_priority_and_no_guess(self):
        ref = seat_reference(model(body='original', seat=True))
        bone, rule = seat_for(model(body='torso'), ref)
        self.assertEqual(('B', 'torso'), (rule, bone['parent']))
        bad = model()
        geometry(bad)['bones'] = []
        self.assertEqual((None, 'no_suitable_parent'), seat_for(bad, ref))

    def test_insertion_preserves_all_original_bytes(self):
        for text in [json.dumps(model(), indent=2)+'\n', json.dumps(model(), separators=(',', ':')), json.dumps(model(), indent='\t').replace('\n', '\r\n')]:
            bone, _ = seat_for(json.loads(text), seat_reference(model(seat=True)))
            after = append_bone(text, bone)
            insertion = ',' + json.dumps(bone, separators=(',', ':'), ensure_ascii=False)
            self.assertEqual(text, after.replace(insertion, '', 1))
            self.assertEqual(geometry(json.loads(text))['bones'], geometry(json.loads(after))['bones'][:-1])

    def test_existing_locator_untouched_and_name_collision_safe(self):
        ref = seat_reference(model(seat=True))
        self.assertEqual((None, 'already_seated'), seat_for(model(seat=True), ref))
        target = model()
        geometry(target)['bones'].append({'name':'locator_seat_1','parent':'body'})
        bone, _ = seat_for(target, ref)
        self.assertEqual('locator_seat_1_cre', bone['name'])

    def test_property_merge_preserves_other_fields(self):
        old = '{\r\n\t"target": "cobblemon:test", "moves": ["1:tackle"]\r\n}\r\n'
        new = add_property(old, 'riding', {'seats':[]})
        self.assertEqual(['1:tackle'], json.loads(new)['moves'])
        self.assertTrue(new.startswith(old[:old.rfind('\r\n}')]))

    def test_named_main_root_with_unparented_accessory_bones(self):
        target = model(root='bb_main', body='accessory')
        geometry(target)['bones'].append({'name':'ornament','pivot':[0,0,0]})
        ref = seat_reference(model(body='missing', seat=True))
        bone, rule = seat_for(target, ref)
        self.assertEqual(('B', 'bb_main'), (rule, bone['parent']))

    def test_missing_reference_does_not_invent_a_seat(self):
        self.assertEqual((None, 'no_reference_seat'), seat_for(model(), None))

    def test_object_locator_translation_preserves_rotation(self):
        source = model(seat=True)
        geometry(source)['bones'][-1]['locators']['seat_1'] = {'offset':[0,10,1], 'rotation':[0,90,0]}
        bone, rule = seat_for(model(pivot=[2,9,0]), seat_reference(source))
        self.assertEqual({'offset':[2,14,1], 'rotation':[0,90,0]}, bone['locators']['seat_1'])

    def test_legacy_jar_supplies_only_locator_not_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'pack';root.mkdir()
            stock=Path(tmp)/'stock.jar';cre=Path(tmp)/'cre.jar';legacy=Path(tmp)/'legacy.jar'
            path='assets/cobblemon/bedrock/pokemon/models/test.geo.json'
            authored=model(pivot=[2,9,0])
            p=root/path;p.parent.mkdir(parents=True);p.write_text(json.dumps(authored,indent=2))
            riding={'behaviours':{'LAND':{'key':'cobblemon:land/horse'}},'seats':[{'locator':'seat_1'}]}
            with zipfile.ZipFile(stock,'w') as z:
                z.writestr('fabric.mod.json',json.dumps({'version':'1.8.1'}))
                z.writestr('data/cobblemon/species/test.json',json.dumps({'riding':riding}))
                z.writestr('com/cobblemon/mod/common/api/riding/behaviour/types/land/HorseBehaviour.class',b'land/horse')
                z.writestr('assets/cobblemon/bedrock/pokemon/resolvers/test.json',json.dumps({'species':'cobblemon:test','variations':[{'model':'cobblemon:test.geo'}]}))
            with zipfile.ZipFile(cre,'w'):pass
            old=model(seat=True);geometry(old)['description']['texture_width']=1024
            with zipfile.ZipFile(legacy,'w') as z:z.writestr(path,json.dumps(old))
            result=run(cre,stock,root,legacy_seat_jars=[legacy])
            self.assertEqual(1,len(result['rule_A']))
            result_doc=json.loads(p.read_text());self.assertEqual(64,geometry(result_doc)['description']['texture_width'])
            self.assertEqual(geometry(authored)['bones'],geometry(result_doc)['bones'][:-1])
            self.assertEqual([2,14,1],geometry(result_doc)['bones'][-1]['locators']['seat_1'])
            before=p.read_bytes();self.assertEqual([],run(cre,stock,root,legacy_seat_jars=[legacy])['changed_files']);self.assertEqual(before,p.read_bytes())

    def test_multiple_geometry_rejected(self):
        d = model();d['minecraft:geometry'] *= 2
        with self.assertRaises(ValueError):seat_reference(d)

    def test_full_import_skin_layers_skip_rules_and_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'pack';root.mkdir()
            riding = {'behaviours': {'LAND':{'key':'cobblemon:land/horse'}}, 'seats':[{'locator':'seat_1'}]}
            def jar(path, files):
                with zipfile.ZipFile(path, 'w') as z:
                    for n, d in files.items():z.writestr(n, d if isinstance(d, bytes) else json.dumps(d))
            stock = Path(tmp)/'stock.jar';cre = Path(tmp)/'cre.jar'
            rp='assets/cobblemon/bedrock/pokemon/resolvers/test.json'
            mp='assets/cobblemon/bedrock/pokemon/models/'
            files={'fabric.mod.json':{'version':'1.8.1'}, 'com/cobblemon/mod/common/api/riding/behaviour/types/land/HorseBehaviour.class': b'land/horse', rp:{'species':'cobblemon:test','variations':[{'model':'cobblemon:test.geo'}, {'aspects':['skin'], 'layers':[{'model':'cobblemon:skin.geo'}]}, {'aspects':['mega'], 'model':'cobblemon:mega.geo'}]}, 'data/cobblemon/species/test.json':{}, 'data/cobblemon/species/already.json':{'riding':riding}, 'data/cobblemon/species/custom.json':{}, 'data/cobblemon/species/invalid.json':{}}
            jar(stock,files)
            incoming={mp+'test.geo.json':model(seat=True)}
            for s in ['test','already','custom','missing','invalid']:incoming['data/cobblemon/species_additions/'+s+'.json']={'target':'cobblemon:'+s,'riding':copy.deepcopy(riding)}
            incoming['data/cobblemon/species_additions/invalid.json']['riding']['behaviours']['LAND']['key']='cobblemon:invalid'
            jar(cre,incoming)
            for n,d in {mp+'skin.geo.json':model(),mp+'mega.geo.json':model(body='torso'), 'data/cobblemon/species_additions/custom.json':{'target':'cobblemon:custom','riding':riding,'moves':['a']},'data/cobblemon/species_additions/test.json':{'target':'cobblemon:test','moves':['b']}}.items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
            first=run(cre,stock,root)
            self.assertEqual(['cobblemon:test'], first['species_added'])
            self.assertEqual(1,len(first['models_copied_cre']))
            self.assertEqual(1,len(first['rule_A']))
            self.assertEqual(1,len(first['rule_B']))
            self.assertEqual('invalid_target',first['species_skipped']['cobblemon:missing'])
            self.assertEqual('stock_already_rideable',first['species_skipped']['cobblemon:already'])
            self.assertEqual('existing_pack_riding',first['species_skipped']['cobblemon:custom'])
            before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            second=run(cre,stock,root)
            self.assertEqual([],second['changed_files'])
            self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()})
            self.assertEqual(['b'],json.loads((root/'data/cobblemon/species_additions/test.json').read_text())['moves'])


if __name__ == '__main__':unittest.main()
