import unittest
from audit_installed_models import legacy_animation_references, legacy_animation_issue


class LegacyAnimationAuditTest(unittest.TestCase):
    def test_crash_report_syntax(self):
        self.assertEqual(legacy_animation_references('bedrock(lycanroc_midday, ground_walk)'), [('lycanroc_midday', 'ground_walk')])
        self.assertEqual(legacy_animation_references('bedrock(zangoose, battle_idle)'), [('zangoose', 'battle_idle')])

    def test_does_not_parse_molang_as_legacy(self):
        self.assertEqual(legacy_animation_references("q.bedrock('zangoose', 'battle_idle')"), [])

    def test_other_group_cannot_supply_missing_animation(self):
        groups = {'other': [('other.animation.json', {'animation.lycanroc_midday.ground_walk'})]}
        self.assertEqual(legacy_animation_issue('lycanroc_midday', 'ground_walk', groups), 'crash_legacy_animation_missing')

    def test_collision_is_not_a_union(self):
        groups = {'lycanroc_midday': [('old/lycanroc_midday.animation.json', {'animation.lycanroc_midday.ground_walk'}), ('new/lycanroc_midday.animation.json', {'animation.lycanroc_midday.ground_idle'})]}
        self.assertEqual(legacy_animation_issue('lycanroc_midday', 'ground_walk', groups), 'crash_legacy_animation_group_collision')

    def test_isolated_group_resolves(self):
        groups = {'isolated': [('isolated.animation.json', {'animation.isolated.ground_walk'})]}
        self.assertIsNone(legacy_animation_issue('isolated', 'ground_walk', groups))


if __name__ == '__main__':
    unittest.main()
