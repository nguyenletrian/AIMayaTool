from __future__ import absolute_import

import os
import shutil
import tempfile
import unittest

from aimayatool.tools.scene.patterns import ScenePattern
from aimayatool.tools.scene.presets import PresetLibrary


class PresetLibraryTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.library = PresetLibrary(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_round_trip_and_sorted_list(self):
        self.library.save("zeta", ScenePattern("z", nodes=["a"]))
        self.library.save("alpha", ScenePattern("a"))
        self.assertEqual(["alpha", "zeta"], self.library.list())
        self.assertEqual("z", self.library.get("zeta").pattern_id)

    def test_duplicate_requires_explicit_overwrite(self):
        self.library.save("one", ScenePattern("a"))
        with self.assertRaises(IOError): self.library.save("one", ScenePattern("b"))
        self.library.save("one", ScenePattern("b"), overwrite=True)
        self.assertEqual("b", self.library.get("one").pattern_id)

    def test_invalid_names_rejected(self):
        for name in ("", ".", "..", "../escape", "a/b", "a\\\\b"):
            with self.assertRaises(ValueError): self.library.path(name)

    def test_delete_and_missing(self):
        self.library.save("one", ScenePattern("a"))
        self.assertTrue(self.library.delete("one"))
        self.assertIsNone(self.library.get("one"))
        self.assertFalse(self.library.delete("one", missing_ok=True))
        with self.assertRaises(IOError): self.library.delete("one")


if __name__ == "__main__":
    unittest.main()
