class WellControl:
    """
    Simulates Kick detection, Gas Migration, and BOP operations.
    """
    def __init__(self):
        self.bop_closed = False
        self.choke_opening = 1.0 # 1.0 = 100% open
        self.kill_mud_density = 0.0
        self.influx_volume = 0.0
        self.influx_active = False
        self.sidpp = 0.0 # Shut-In Drill Pipe Pressure
        self.sicp = 0.0 # Shut-In Casing Pressure

    def check_for_kick(self, bhp, pore_pressure):
        """
        Returns True if a kick is occurring.
        """
        if bhp < pore_pressure:
            return True
        return False

    def update_influx(self, bhp, pore_pressure, permeability, dt):
        """
        Calculates influx volume based on underbalance and permeability.
        """
        if bhp < pore_pressure:
            underbalance = pore_pressure - bhp
            # Simplified Darcy's law for flow into wellbore
            flow_rate = (permeability * underbalance) * 0.001 # m3/s arbitrary scaling
            self.influx_volume += flow_rate * dt
            self.influx_active = True
            return flow_rate * dt
        else:
            self.influx_active = False
            return 0.0

    def gas_migration(self, dt):
        """
        Simulates gas rising in the annulus.
        """
        if self.influx_volume > 0:
            # Gas rises at approx 0.1 - 0.3 m/s
            migration_rate = 0.2 # m/s
            # In a full simulation, we'd track the gas bubble depth
            pass

    def close_bop(self):
        self.bop_closed = True

    def open_bop(self):
        self.bop_closed = False

    def calculate_shut_in_pressures(self, pore_pressure, hydrostatic_drillpipe, hydrostatic_annulus):
        """
        SIDPP = Pore Pressure - Hydrostatic (Drill Pipe)
        SICP = Pore Pressure - Hydrostatic (Annulus with Influx)
        """
        if self.bop_closed:
            self.sidpp = max(0.0, pore_pressure - hydrostatic_drillpipe)
            self.sicp = max(0.0, pore_pressure - hydrostatic_annulus)
        else:
            self.sidpp = 0.0
            self.sicp = 0.0
