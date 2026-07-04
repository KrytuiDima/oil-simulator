import unittest
from engine.lifecycle import WellLifecycle

class TestLifecycle(unittest.TestCase):
    def test_stage_progression(self):
        wl = WellLifecycle()
        self.assertEqual(wl.current_stage, "Site Survey & Permitting")
        wl.next_stage()
        self.assertEqual(wl.current_stage, "Rig Mobilization")

    def test_drilling_status(self):
        wl = WellLifecycle()
        # Stage 0 (Site Survey) is not drilling
        self.assertFalse(wl.is_drilling_active())
        # Stage 3 (Conductor Drilling) is drilling
        for _ in range(3): wl.next_stage()
        self.assertTrue(wl.is_drilling_active())

if __name__ == "__main__":
    unittest.main()
