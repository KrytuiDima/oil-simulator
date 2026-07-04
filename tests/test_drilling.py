import unittest
from engine.drilling import DrillingMechanics

class TestDrilling(unittest.TestCase):
    def test_rop_sensitivity(self):
        ucs = 50 # MPa
        bit_d = 8.5 # inches

        rop_low = DrillingMechanics.calculate_rop(5, 60, bit_d, ucs, 0, 1.0)
        rop_high = DrillingMechanics.calculate_rop(15, 120, bit_d, ucs, 0, 1.0)

        self.assertGreater(rop_high, rop_low)

    def test_bit_wear(self):
        wear_inc = DrillingMechanics.calculate_bit_wear(20, 0.5, 50.0, 1.0)
        self.assertGreater(wear_inc, 0)

    def test_torque(self):
        torque = DrillingMechanics.calculate_torque(10, 8.5, 100, 0.3, 50.0)
        self.assertGreater(torque, 0)

if __name__ == "__main__":
    unittest.main()
