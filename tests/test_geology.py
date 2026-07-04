import unittest
from models.geology import FormationGenerator, Layer

class TestGeology(unittest.TestCase):
    def test_formation_generation(self):
        total_depth = 3000
        layers = FormationGenerator.generate(total_depth)

        self.assertTrue(len(layers) > 0)
        self.assertEqual(layers[0].top, 0.0)
        self.assertEqual(layers[-1].bottom, total_depth)

        for layer in layers:
            self.assertGreater(layer.ucs, 0)
            self.assertGreater(layer.pore_pressure_grad, 0)
            self.assertGreater(layer.fracture_grad, layer.pore_pressure_grad)
            self.assertIn(layer.name, FormationGenerator.LITHOLOGIES.keys())

if __name__ == "__main__":
    unittest.main()
