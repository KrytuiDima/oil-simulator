import random

class Layer:
    """
    Represent a geological formation layer with physical and mechanical properties.
    """
    def __init__(self, name, top_depth, bottom_depth):
        self.name = name
        self.top = top_depth
        self.bottom = bottom_depth

        # Mechanical Properties
        self.ucs = 0.0             # Unconfined Compressive Strength (MPa)
        self.young_modulus = 0.0   # (GPa)
        self.poisson_ratio = 0.0
        self.hardness = 0.0        # Mohs or similar scale
        self.abrasivity = 0.0      # Coefficient for bit wear

        # Reservoir Properties
        self.porosity = 0.0        # %
        self.permeability = 0.0    # mD
        self.oil_saturation = 0.0  # %
        self.gas_saturation = 0.0  # %
        self.water_saturation = 0.0 # %

        # Pressure & Temperature
        self.pore_pressure_grad = 0.0 # bar / 10m
        self.fracture_grad = 0.0      # bar / 10m
        self.temp_grad = 0.03         # °C / m (standard geothermal)

        # Physical Characteristics
        self.density = 0.0            # g/cm3 (matrix density)
        self.mineralogy = {}          # e.g., {"Quartz": 0.6, "Clay": 0.4}
        self.natural_fractures = 0.0   # Fracture density index (0 to 1)

    def __repr__(self):
        return f"<Layer {self.name} ({self.top}-{self.bottom}m)>"

class FormationGenerator:
    """
    Procedurally generates a formation sequence for a well.
    """
    LITHOLOGIES = {
        "Sandstone": {"ucs": (20, 60), "por": (15, 30), "perm": (100, 2000), "abr": 0.4, "dens": 2.65},
        "Shale": {"ucs": (10, 40), "por": (5, 15), "perm": (0.001, 0.1), "abr": 0.2, "dens": 2.70},
        "Limestone": {"ucs": (60, 150), "por": (5, 20), "perm": (1, 100), "abr": 0.6, "dens": 2.71},
        "Dolomite": {"ucs": (80, 200), "por": (5, 15), "perm": (1, 50), "abr": 0.7, "dens": 2.85},
        "Granite": {"ucs": (150, 250), "por": (1, 3), "perm": (0.0001, 0.01), "abr": 0.9, "dens": 2.65}
    }

    @staticmethod
    def generate(total_depth):
        layers = []
        current_depth = 0.0

        while current_depth < total_depth:
            litho_name = random.choice(list(FormationGenerator.LITHOLOGIES.keys()))
            props = FormationGenerator.LITHOLOGIES[litho_name]

            thickness = random.uniform(50, 300)
            bottom = min(current_depth + thickness, total_depth)

            layer = Layer(litho_name, current_depth, bottom)
            layer.ucs = random.uniform(*props["ucs"])
            layer.porosity = random.uniform(*props["por"])
            layer.permeability = random.uniform(*props["perm"])
            layer.abrasivity = props["abr"] + random.uniform(-0.1, 0.1)
            layer.density = props["dens"]

            # Gradients increase with depth
            base_pore_grad = 1.03 # bar/10m (hydrostatic)
            layer.pore_pressure_grad = base_pore_grad + (current_depth / 5000) * random.uniform(0.1, 0.5)
            layer.fracture_grad = layer.pore_pressure_grad + random.uniform(0.4, 0.8)

            layer.young_modulus = layer.ucs * 0.5 # GPa, simplified
            layer.poisson_ratio = random.uniform(0.2, 0.35)

            # Saturation (simplified)
            if litho_name == "Sandstone" and current_depth > 1500:
                roll = random.random()
                if roll > 0.8:
                    layer.oil_saturation = 0.7
                    layer.water_saturation = 0.3
                elif roll > 0.6:
                    layer.gas_saturation = 0.8
                    layer.water_saturation = 0.2
                else:
                    layer.water_saturation = 1.0
            else:
                layer.water_saturation = 1.0

            layers.append(layer)
            current_depth = bottom

        return layers
