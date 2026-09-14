from aimayatool.tools.setup import naming


def test_sanitize_legacy_name_replaces_legacy_fbx_tokens_and_punctuation():
    assert naming.sanitize_legacy_name("ArmFBXASC046End.FBXASC032[01]FBXASC045JNT") == "Arm_End__01__JNT"


def test_sanitize_legacy_name_preserves_other_characters():
    assert naming.sanitize_legacy_name("L_Hand_JNT") == "L_Hand_JNT"


def test_sanitize_legacy_name_requires_value():
    try:
        naming.sanitize_legacy_name(None)
    except ValueError as exc:
        assert "Name is required" in str(exc)
    else:
        raise AssertionError("Expected ValueError for None name")
