import math

class HydraulicsEngine:
    """
    Calculates pressure losses using detailed rheological models and Reynolds numbers.
    """
    @staticmethod
    def calculate_reynolds(density, velocity, diameter, viscosity):
        """
        Calculates Reynolds number for pipe flow.
        density: kg/m3
        velocity: m/s
        diameter: m
        viscosity: Pa.s (1 cP = 0.001 Pa.s)
        """
        if viscosity <= 0 or diameter <= 0:
            return 0
        return (density * velocity * diameter) / viscosity

    @staticmethod
    def get_friction_factor(reynolds):
        """
        Returns friction factor using a simplified Moody correlation.
        """
        if reynolds < 2100:
            return 64 / reynolds
        else:
            # Blasius equation for turbulent flow in smooth pipes
            return 0.3164 / (reynolds**0.25)

    @staticmethod
    def calculate_pressure_loss(density_sg, flow_lpm, id_inch, length_m, pv_cp, yp_lb):
        """
        Detailed pressure loss calculation.
        """
        if length_m <= 0 or id_inch <= 0 or flow_lpm <= 0:
            return 0.0

        # Convert units to SI
        density = density_sg * 1000 # kg/m3
        diameter = id_inch * 0.0254 # m
        area = math.pi * (diameter / 2)**2
        velocity = (flow_lpm / 60000) / area # m/s

        # Effective viscosity for Bingham Plastic
        # tau = YP + PV * gamma_dot
        gamma_dot = 8 * velocity / diameter # shear rate at wall
        viscosity_eff = (pv_cp * 0.001) + (yp_lb * 0.4788 / gamma_dot) # Pa.s

        re = HydraulicsEngine.calculate_reynolds(density, velocity, diameter, viscosity_eff)
        f = HydraulicsEngine.get_friction_factor(re)

        # Darcy-Weisbach equation
        # deltaP = f * (L/D) * (rho * v^2 / 2)
        p_loss_pa = f * (length_m / diameter) * (density * velocity**2 / 2)
        return p_loss_pa / 100000 # bar

    @staticmethod
    def calculate_hydrostatic_pressure(mud_density, true_vertical_depth):
        return (mud_density * true_vertical_depth) / 10.197

    @staticmethod
    def calculate_ecd(bhp, true_vertical_depth):
        if true_vertical_depth <= 0: return 0.0
        return (bhp * 10.197) / true_vertical_depth

    @staticmethod
    def calculate_annular_pressure_loss(density_sg, flow_lpm, hole_inch, pipe_od_inch, length_m, pv_cp, yp_lb):
        """
        Detailed annular pressure loss calculation.
        """
        if length_m <= 0 or hole_inch <= pipe_od_inch or flow_lpm <= 0:
            return 0.0

        density = density_sg * 1000
        d_hyd = (hole_inch - pipe_od_inch) * 0.0254 # Hydraulic diameter
        area = math.pi * ((hole_inch * 0.0254 / 2)**2 - (pipe_od_inch * 0.0254 / 2)**2)
        velocity = (flow_lpm / 60000) / area

        gamma_dot = 12 * velocity / d_hyd # Shear rate in annulus
        viscosity_eff = (pv_cp * 0.001) + (yp_lb * 0.4788 / gamma_dot)

        re = HydraulicsEngine.calculate_reynolds(density, velocity, d_hyd, viscosity_eff)
        f = HydraulicsEngine.get_friction_factor(re)

        p_loss_pa = f * (length_m / d_hyd) * (density * velocity**2 / 2)
        return p_loss_pa / 100000
