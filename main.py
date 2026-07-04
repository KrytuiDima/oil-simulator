import time
import sys
from models.geology import FormationGenerator
from engine.hydraulics import HydraulicsEngine
from engine.drilling import DrillingMechanics
from engine.safety import WellControl
from engine.lifecycle import WellLifecycle
from engine.economy import EconomyEngine
from engine.ai_consultant import AIConsultant

class DrillMasterGame:
    def __init__(self):
        self.total_depth = 2500
        self.geology = FormationGenerator.generate(self.total_depth)
        self.lifecycle = WellLifecycle()
        self.hydraulics = HydraulicsEngine()
        self.mechanics = DrillingMechanics()
        self.safety = WellControl()
        self.economy = EconomyEngine()
        self.ai = AIConsultant()

        # Well State
        self.current_depth = 0.0
        self.bit_depth = 0.0
        self.mud_density = 1.15 # SG
        self.pv = 15
        self.yp = 10
        self.flow_rate = 0.0 # LPM

        self.wob = 0.0 # tons
        self.rpm = 0.0
        self.bit_wear = 0.0

        self.running = True
        self.last_update = time.time()

    def get_current_layer(self):
        for layer in self.geology:
            if layer.top <= self.current_depth <= layer.bottom:
                return layer
        return self.geology[-1]

    def render(self, state, ai_messages):
        # Clear screen
        print("\033[H\033[J", end="")

        print("\033[93m" + "="*80)
        print(f" 🏗  DRILL MASTER: OIL & GAS ENGINEER        Budget: ${self.economy.budget:,.0f}")
        print("="*80 + "\033[0m")

        # Header Info & Rig Visual
        rig_art = [
            "      ▲      ",
            "     / \\     ",
            "    /   \\    ",
            "   / [I] \\   ",
            "  /_______\\  "
        ]

        print(f" \033[94mSTAGE:\033[0m {self.lifecycle.current_stage}")
        print(f" \033[94mDEPTH:\033[0m {self.current_depth:8.2f} m  | \033[94mROP:\033[0m {state['rop']:8.2f} m/h")
        print(f" \033[94mWEAR:\033[0m  {self.bit_wear*100:8.1f} %  | \033[94mECD:\033[0m {state['ecd']:8.3f} SG")
        print("-" * 80)

        # Wellbore Visualization
        print(" \033[1mWELLBORE & RIG VIEW:\033[0m")
        visible_range = 12
        start_view = max(0, int(self.current_depth / 10) - 6)

        for idx, i in enumerate(range(start_view, start_view + visible_range)):
            depth_label = i * 10
            # Find layer for this depth
            l_name = "Unknown"
            for l in self.geology:
                if l.top <= depth_label <= l.bottom:
                    l_name = l.name
                    break

            pipe = "  ||  "
            if depth_label > self.current_depth:
                pipe = "      "
            elif depth_label == int(self.current_depth / 10) * 10:
                pipe = " \033[91m-⚙-\033[0m " # Bit visualization

            color = "\033[0m"
            if l_name == "Sandstone": color = "\033[93m" # Yellow
            elif l_name == "Shale": color = "\033[90m"    # Grey
            elif l_name == "Limestone": color = "\033[97m" # White
            elif l_name == "Granite": color = "\033[91m"   # Red

            rig_line = rig_art[idx] if idx < len(rig_art) else "             "
            print(f"{rig_line} {depth_label:4}m {color}[{l_name:12}]{pipe}\033[0m")

        print("-" * 80)
        # AI Console
        print(" \033[1;92m🤖 AI CONSULTANT:\033[0m")
        if not ai_messages:
            print(" > System operating within normal parameters.")
        for msg in ai_messages[-3:]:
            print(f" > {msg}")

        print("\033[93m" + "=" * 80 + "\033[0m")
        print(" \033[1mCONTROLS:\033[0m [W/S] WOB  [A/D] RPM  [Q/E] Flow  [Space] Next Stage  [X] Exit")

    def update(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # Convert seconds to game hours (1 sec = 1 min game time)
        game_dt_hrs = dt / 60.0

        layer = self.get_current_layer()

        # Hydraulics
        hydrostatic = self.hydraulics.calculate_hydrostatic_pressure(self.mud_density, self.current_depth)
        ann_loss = self.hydraulics.calculate_annular_pressure_loss(
            self.mud_density, self.flow_rate, 8.5, 5.0, self.current_depth, self.pv, self.yp
        )
        bhp = hydrostatic + ann_loss
        ecd = self.hydraulics.calculate_ecd(bhp, self.current_depth)

        # Drilling
        if self.lifecycle.is_drilling_active() and self.flow_rate > 500:
            clean_eff = min(1.0, self.flow_rate / 2500.0)
            rop = self.mechanics.calculate_rop(self.wob, self.rpm, 8.5, layer.ucs, self.bit_wear, clean_eff)

            # Update Depth
            depth_inc = (rop * game_dt_hrs)
            self.current_depth += depth_inc
            self.bit_depth = self.current_depth

            # Bit Wear
            self.bit_wear += self.mechanics.calculate_bit_wear(rop, layer.abrasivity, game_dt_hrs)
        else:
            rop = 0.0

        # Safety
        pore_pressure = (layer.pore_pressure_grad * self.current_depth) / 10.0
        kick_active = self.safety.check_for_kick(bhp, pore_pressure)
        if kick_active:
            self.safety.update_influx(bhp, pore_pressure, layer.permeability, dt)

        # Economy
        self.economy.apply_daily_costs(game_dt_hrs / 24.0)
        if rop > 0:
            self.economy.apply_drilling_costs(game_dt_hrs)

        # AI
        state = {
            "rop": rop,
            "wob": self.wob,
            "rpm": self.rpm,
            "flow": self.flow_rate,
            "bit_wear": self.bit_wear,
            "kick_active": kick_active,
            "ecd": ecd,
            "fracture_grad": layer.fracture_grad,
            "ucs": layer.ucs,
            "cleaning_efficiency": (self.flow_rate / 2500.0) if self.flow_rate > 0 else 0
        }
        ai_messages = self.ai.analyze(state)

        return state, ai_messages

if __name__ == "__main__":
    import select
    import tty
    import termios

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                return sys.stdin.read(1)
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    game = DrillMasterGame()

    try:
        while game.running:
            key = get_key()
            if key == 'q': game.flow_rate = min(3500, game.flow_rate + 100)
            elif key == 'e': game.flow_rate = max(0, game.flow_rate - 100)
            elif key == 'w': game.wob = min(30, game.wob + 1)
            elif key == 's': game.wob = max(0, game.wob - 1)
            elif key == 'a': game.rpm = min(200, game.rpm + 10)
            elif key == 'd': game.rpm = max(0, game.rpm - 10)
            elif key == ' ': game.lifecycle.next_stage()
            elif key == 'x': break

            state, msgs = game.update()
            game.render(state, msgs)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nSimulation Terminated.")
