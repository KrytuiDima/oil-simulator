import unittest
from engine.safety import WellControl

class TestSafety(unittest.TestCase):
    def test_kick_detection(self):
        wc = WellControl()
        self.assertTrue(wc.check_for_kick(100, 110))
        self.assertFalse(wc.check_for_kick(120, 110))

    def test_influx(self):
        wc = WellControl()
        wc.update_influx(100, 110, 500, 1.0)
        self.assertGreater(wc.influx_volume, 0)
        self.assertTrue(wc.influx_active)

    def test_shut_in(self):
        wc = WellControl()
        wc.close_bop()
        # Pore 200, Hydro DP 180 -> SIDPP 20
        wc.calculate_shut_in_pressures(200, 180, 170)
        self.assertEqual(wc.sidpp, 20)
        self.assertEqual(wc.sicp, 30)

if __name__ == "__main__":
    unittest.main()
