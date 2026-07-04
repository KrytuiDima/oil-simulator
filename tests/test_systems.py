import unittest
from engine.economy import EconomyEngine
from engine.ai_consultant import AIConsultant

class TestSystems(unittest.TestCase):
    def test_economy(self):
        econ = EconomyEngine(1000000)
        econ.apply_daily_costs(1)
        self.assertEqual(econ.budget, 1000000 - 60000)

    def test_ai_rop_drop(self):
        ai = AIConsultant()
        # High WOB/RPM but low ROP and high bit wear
        msgs = ai.analyze({"rop": 1.0, "wob": 10, "rpm": 60, "bit_wear": 0.9})
        self.assertTrue(any("bit wear" in m.lower() for m in msgs))

    def test_ai_kick(self):
        ai = AIConsultant()
        msgs = ai.analyze({"kick_active": True})
        self.assertTrue(any("gain" in m.lower() for m in msgs))

if __name__ == "__main__":
    unittest.main()
