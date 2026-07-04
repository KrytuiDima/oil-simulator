import math

class DrillingMechanics:
    """
    Detailed Drilling Mechanics using MSE and Warren model.
    """
    @staticmethod
    def calculate_mse(wob_tons, rpm, torque_knm, rop_mh, bit_diameter_inch):
        """
        Mechanical Specific Energy (MPa).
        MSE = WOB/Area + (120 * PI * RPM * Torque) / (Area * ROP)
        """
        area = math.pi * (bit_diameter_inch * 0.0254 / 2)**2
        if rop_mh <= 0:
            return 0.0

        wob_n = wob_tons * 9806
        torque_nm = torque_knm * 1000
        rop_ms = rop_mh / 3600

        mse = (wob_n / area) + (2 * math.pi * (rpm / 60) * torque_nm) / (area * rop_ms)
        return mse / 1000000 # MPa

    @staticmethod
    def calculate_rop(wob, rpm, bit_diameter, ucs, bit_wear, clean_efficiency):
        """
        Improved ROP model.
        """
        if bit_diameter <= 0 or ucs <= 0: return 0.0

        # d-exponent style normalized ROP
        wob_norm = (wob * 2000) / (bit_diameter * 1000) # lbs/inch roughly

        # Base ROP depends on rock strength and drilling intensity
        base_rop = (rpm**0.7 * wob**1.2) / (ucs * bit_diameter * 0.05)

        # Cleaning efficiency effect
        # If flow is too low, ROP is capped by chip removal
        rop = base_rop * clean_efficiency

        # Wear effect: exponential decay
        wear_factor = math.exp(-2.0 * bit_wear)

        return max(0.0, rop * wear_factor)

    @staticmethod
    def calculate_bit_wear(rop, abrasivity, ucs, duration_hrs):
        # Wear depends on work done and rock hardness/abrasivity
        wear_rate = (rop * abrasivity * (ucs/50)) / 2000.0
        return wear_rate * duration_hrs

    @staticmethod
    def calculate_torque(wob, bit_diameter, rpm, friction_coeff, ucs):
        # Torque has a component related to rock cutting and one to friction
        # T_cutting = k * WOB * D * sqrt(ROP/RPM)
        torque = 0.4 * wob * (bit_diameter * 0.0254) * friction_coeff * (ucs / 100)
        torque += (rpm / 500.0)
        return torque

    @staticmethod
    def calculate_hook_load(string_depth_m, mud_density_sg):
        # Hook Load = Weight in air * Buoyancy Factor
        # Assume drill pipe weight 30 kg/m
        weight_air = string_depth_m * 30 * 9.806 / 1000 # kN
        buoyancy_factor = 1 - (mud_density_sg / 7.85) # density of steel 7.85
        return (weight_air * buoyancy_factor) / 9.806 # convert back to tons
