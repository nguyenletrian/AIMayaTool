from __future__ import absolute_import
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from aimayatool.tools.scene import match_pairs

class MatchPairsTests(unittest.TestCase):
    def test_normalize_and_pairs(self):
        self.assertEqual(match_pairs.normalize_names(" A\n\nB "), ["A", "B"])
        self.assertEqual(match_pairs.pair_names(["A", "B"], "X\nY"), [("A", "X"), ("B", "Y")])
        self.assertRaises(ValueError, match_pairs.pair_names, ["A"], ["X", "Y"])

    def test_replacement_map(self):
        self.assertEqual(match_pairs.replacement_map("A\nB", "X\nY"), {"A": "X", "B": "Y"})

    def test_transfer_xml_names_exact_only(self):
        root = tempfile.mkdtemp()
        src, dst = os.path.join(root, "skin.xml"), os.path.join(root, "skin_transferred.xml")
        with open(src, "w") as stream:
            stream.write('<root source="A" untouched="A_extra"><item> B </item><item>A_extra</item></root>')
        match_pairs.transfer_xml_names(src, dst, ["A", "B"], ["X", "Y"])
        tree = ET.parse(dst); r = tree.getroot()
        self.assertEqual(r.attrib["source"], "X"); self.assertEqual(r.attrib["untouched"], "A_extra")
        self.assertEqual(r[0].text.strip(), "Y"); self.assertEqual(r[1].text, "A_extra")

if __name__ == "__main__":
    unittest.main()
