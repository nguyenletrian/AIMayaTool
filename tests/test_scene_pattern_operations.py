from __future__ import absolute_import

import os
import tempfile
import unittest

from aimayatool.tools.scene.operations import create_pattern, edit_pattern, load_pattern, save_pattern


class ScenePatternOperationTests(unittest.TestCase):
    def test_create_and_edit_are_explicit_and_non_mutating(self):
        source = create_pattern("basic", label="Basic", nodes=[{"name": "root"}], metadata={"category": "setup"})
        edited = edit_pattern(source, label="Edited", metadata={"category": "scene"})
        self.assertEqual(source.label, "Basic")
        self.assertEqual(source.metadata, {"category": "setup"})
        self.assertEqual(edited.pattern_id, "basic")
        self.assertEqual(edited.label, "Edited")
        self.assertEqual(edited.nodes, [{"name": "root"}])
        self.assertEqual(edited.metadata, {"category": "scene"})

    def test_save_load_round_trip_and_overwrite_guard(self):
        pattern = create_pattern("roundtrip", label="Round Trip", nodes=[{"name": "root", "type": "transform"}])
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "pattern.json")
            saved = save_pattern(pattern, path)
            self.assertEqual(saved, os.path.abspath(path))
            self.assertEqual(load_pattern(path).to_dict(), pattern.to_dict())
            with self.assertRaises(IOError):
                save_pattern(pattern, path)
            save_pattern(edit_pattern(pattern, label="Updated"), path, overwrite=True)
            self.assertEqual(load_pattern(path).label, "Updated")

    def test_save_requires_existing_parent_directory(self):
        pattern = create_pattern("missing-parent")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "missing", "pattern.json")
            with self.assertRaises(IOError):
                save_pattern(pattern, path)


if __name__ == "__main__":
    unittest.main()
