class EconomyEngine:
    """
    Tracks financial performance, costs, and revenues.
    """
    def __init__(self, initial_budget=10000000):
        self.budget = initial_budget
        self.total_spent = 0.0
        self.revenue = 0.0

        # Costs (USD)
        self.daily_rig_rate = 50000.0
        self.personnel_daily = 10000.0
        self.bit_cost_pdc = 25000.0
        self.mud_cost_per_m3 = 500.0
        self.fuel_cost_per_hr = 1200.0

    def apply_daily_costs(self, dt_days):
        cost = (self.daily_rig_rate + self.personnel_daily) * dt_days
        self._spend(cost)
        return cost

    def apply_drilling_costs(self, dt_hrs):
        cost = self.fuel_cost_per_hr * dt_hrs
        self._spend(cost)
        return cost

    def buy_bit(self):
        self._spend(self.bit_cost_pdc)
        return self.bit_cost_pdc

    def add_revenue(self, amount):
        self.revenue += amount
        self.budget += amount

    def _spend(self, amount):
        self.budget -= amount
        self.total_spent += amount

    def get_status(self):
        return {
            "budget": round(self.budget, 2),
            "spent": round(self.total_spent, 2),
            "revenue": round(self.revenue, 2)
        }
