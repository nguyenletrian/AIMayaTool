from __future__ import absolute_import

import unittest

from aimayatool import registry


class RegistryActionStateTests(unittest.TestCase):
    def setUp(self):
        registry._RECENT_ACTIONS[:] = []
        registry._FAVORITE_ACTIONS.clear()
        registry._ACTIONS.clear()

    def test_recent_actions_promote_duplicates_and_bound_limit(self):
        registry.mark_recent_action("setup", "freeze", "Freeze", limit=2)
        registry.mark_recent_action("skinning", "prune", "Prune", limit=2)
        result = registry.mark_recent_action("setup", "freeze", "Freeze", limit=2)
        self.assertEqual(
            (("setup", "freeze"), ("skinning", "prune")),
            tuple((item["group_id"], item["action_id"]) for item in result),
        )

    def test_favorite_actions_toggle_with_stable_identity(self):
        registry.set_favorite_action("scene", "build", "Build", True)
        self.assertEqual("build", registry.favorite_actions()[0]["action_id"])
        registry.set_favorite_action("scene", "build", "Build", False)
        self.assertEqual((), registry.favorite_actions())

    def test_action_identity_validation(self):
        with self.assertRaisesRegex(ValueError, "Unknown group"):
            registry.mark_recent_action("missing", "run", "Run")
        with self.assertRaisesRegex(ValueError, "Action id is required"):
            registry.mark_recent_action("setup", "", "Run")
        with self.assertRaisesRegex(ValueError, "Action label is required"):
            registry.mark_recent_action("setup", "run", "")
        registry.mark_recent_action("setup", "run", "Run")
        with self.assertRaisesRegex(ValueError, "Action label changed"):
            registry.set_favorite_action("setup", "run", "Different", True)

    def test_group_state_remains_available(self):
        registry.mark_recent("setup")
        registry.set_favorite("setup", True)
        self.assertEqual("setup", registry.recent_groups()[0]["id"])
        self.assertIn("setup", tuple(item["id"] for item in registry.favorite_groups()))


if __name__ == "__main__":
    unittest.main()
