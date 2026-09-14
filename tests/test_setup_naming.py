import unittest

from aimayatool.tools.setup import naming


class SetupNamingTests(unittest.TestCase):
    def test_sanitize_legacy_name_replaces_legacy_fbx_tokens_and_punctuation(self):
        self.assertEqual(
            naming.sanitize_legacy_name("ArmFBXASC046End.FBXASC032[01]FBXASC045JNT"),
            "Arm_End___01__JNT",
        )

    def test_sanitize_legacy_name_preserves_other_characters(self):
        self.assertEqual(naming.sanitize_legacy_name("L_Hand_JNT"), "L_Hand_JNT")

    def test_sanitize_legacy_name_requires_value(self):
        with self.assertRaisesRegex(ValueError, "Name is required"):
            naming.sanitize_legacy_name(None)


if __name__ == "__main__":
    unittest.main()
