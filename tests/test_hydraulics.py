import unittest
from engine.hydraulics import HydraulicsEngine

class TestHydraulics(unittest.TestCase):
    def test_hydrostatic(self):
        density = 1.20 # SG
        tvd = 1000 # m
        pressure = HydraulicsEngine.calculate_hydrostatic_pressure(density, tvd)
        self.assertAlmostEqual(pressure, 117.68, places=1)

    def test_ecd(self):
        bhp = 130 # bar
        tvd = 1000 # m
        ecd = HydraulicsEngine.calculate_ecd(bhp, tvd)
        self.assertAlmostEqual(ecd, 1.325, places=2)

    def test_pressure_losses(self):
        loss_pipe = HydraulicsEngine.calculate_pressure_loss(1.2, 2000, 4.0, 1000, 20, 15)
        loss_ann = HydraulicsEngine.calculate_annular_pressure_loss(1.2, 2000, 8.5, 5.0, 1000, 20, 15)
        self.assertGreater(loss_pipe, 0)
        self.assertGreater(loss_ann, 0)

if __name__ == "__main__":
    unittest.main()
