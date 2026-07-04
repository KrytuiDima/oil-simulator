class AIConsultant:
    """
    Analyzes parameters and provides diagnostic feedback by correlating multiple variables.
    """
    def __init__(self):
        self.history = []

    def analyze(self, state):
        self.history.append(state)
        if len(self.history) > 10:
            self.history.pop(0)

        messages = []

        # Current values
        rop = state.get("rop", 0)
        wob = state.get("wob", 0)
        rpm = state.get("rpm", 0)
        torque = state.get("torque", 0)
        flow = state.get("flow", 0)
        bit_wear = state.get("bit_wear", 0)
        clean_eff = state.get("cleaning_efficiency", 1.0)
        ucs = state.get("ucs", 0)

        # 1. ROP Analysis
        if rop < 2.0 and wob > 5 and rpm > 40:
            # Low ROP despite energy input
            if bit_wear > 0.7:
                messages.append("AI Diagnostic: ROP is critically low. High bit wear detected. Diamonds are likely worn or matrix is damaged.")
            elif clean_eff < 0.5:
                messages.append(f"AI Diagnostic: Pack-off risk! Cleaning efficiency is only {clean_eff*100:.1f}%. Cuttings are regrinding, not being removed.")
            elif ucs > 150:
                messages.append(f"AI Diagnostic: Hard rock encounter. Formation UCS is {ucs:.0f} MPa. WOB/RPM parameters are suboptimal for this lithology.")
            else:
                messages.append("AI Diagnostic: ROP stalling. Possible balling or formation change.")

        # 2. Safety Analysis
        if state.get("kick_active"):
            messages.append("AI EMERGENCY: POSITIVE PIT GAIN! Pore pressure exceeds BHP. Activate BOP and implement Driller's Method.")

        if state.get("ecd", 0) > state.get("fracture_grad", 99):
            messages.append("AI WARNING: LOST CIRCULATION. ECD exceeds fracture gradient. Mud is migrating into induced fractures.")

        # 3. Dynamic Trends (comparing to previous state)
        if len(self.history) > 1:
            prev = self.history[-2]
            if torque > prev.get("torque", 0) * 1.5 and rop < prev.get("rop", 1):
                 messages.append("AI Diagnostic: Torque spike with ROP drop. Stick-slip vibration or bit sub-component failure suspected.")

        return messages
