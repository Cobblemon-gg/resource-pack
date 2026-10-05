import json
import tempfile
import unittest
from pathlib import Path

from cre_import import runtime_updates


class RuntimeImportTest(unittest.TestCase):
    def resources(self):
        return {
            'data/cre/function/tick.mcfunction': b'# upstream function\n',
            'data/cre/predicate/is_in_air.json': b'{}',
            'data/cre/predicate/is_riding.json': b'{}',
            'data/minecraft/tags/function/tick.json': b'{"values":["cre:tick"]}',
        }

    def test_preserves_other_tick_hooks_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tag = root / 'data/minecraft/tags/function/tick.json'
            tag.parent.mkdir(parents=True)
            tag.write_text('{"replace":false,"values":["atlas:tick"]}')
            for n, data in runtime_updates(self.resources(), root).items():
                p = root / n
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            self.assertEqual({'replace': False, 'values': ['atlas:tick', 'cre:tick']}, json.loads(tag.read_text()))
            self.assertEqual({}, runtime_updates(self.resources(), root))

    def test_initial_import_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n, data in runtime_updates(self.resources(), root).items():
                p = root / n
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            self.assertEqual({}, runtime_updates(self.resources(), root))

    def test_incomplete_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                runtime_updates({'data/cre/function/tick.mcfunction': b''}, Path(tmp))

    def test_old_jar_without_runtime_is_supported(self):
        self.assertEqual({}, runtime_updates({}, Path('.')))
