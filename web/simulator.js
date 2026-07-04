class Geology {
    static LITHOLOGIES = {
        "Sandstone": { ucs: [20, 60], por: [15, 30], perm: [100, 2000], abr: 0.4, color: "#facc15" },
        "Shale": { ucs: [10, 40], por: [5, 15], perm: [0.001, 0.1], abr: 0.2, color: "#64748b" },
        "Limestone": { ucs: [60, 150], por: [5, 20], perm: [1, 100], abr: 0.6, color: "#e2e8f0" },
        "Dolomite": { ucs: [80, 200], por: [5, 15], perm: [1, 50], abr: 0.7, color: "#94a3b8" },
        "Granite": { ucs: [150, 250], por: [1, 3], perm: [0.0001, 0.01], abr: 0.9, color: "#f87171" }
    };

    static generate(totalDepth) {
        let layers = [];
        let currentDepth = 0;
        while (currentDepth < totalDepth) {
            let keys = Object.keys(Geology.LITHOLOGIES);
            let litho = keys[Math.floor(Math.random() * keys.length)];
            let props = Geology.LITHOLOGIES[litho];
            let thickness = 50 + Math.random() * 250;
            let bottom = Math.min(currentDepth + thickness, totalDepth);

            layers.push({
                name: litho,
                top: currentDepth,
                bottom: bottom,
                ucs: props.ucs[0] + Math.random() * (props.ucs[1] - props.ucs[0]),
                porosity: props.por[0] + Math.random() * (props.por[1] - props.por[0]),
                permeability: props.perm[0] + Math.random() * (props.perm[1] - props.perm[0]),
                abrasivity: props.abr + (Math.random() * 0.2 - 0.1),
                color: props.color,
                pore_grad: 1.03 + (currentDepth / 5000) * (0.1 + Math.random() * 0.4),
                fracture_grad: 1.5 + (currentDepth / 5000) * 0.5
            });
            currentDepth = bottom;
        }
        return layers;
    }
}

class Hydraulics {
    static calculatePressureLoss(density_sg, flow_lpm, id_inch, length_m, pv, yp) {
        if (length_m <= 0 || id_inch <= 0 || flow_lpm <= 0) return 0;
        let density = density_sg * 1000;
        let d = id_inch * 0.0254;
        let v = (flow_lpm / 60000) / (Math.PI * (d / 2)**2);
        let gamma = 8 * v / d;
        let mu_eff = (pv * 0.001) + (yp * 0.4788 / gamma);
        let re = (density * v * d) / mu_eff;
        let f = (re < 2100) ? (64 / re) : (0.3164 / Math.pow(re, 0.25));
        return (f * (length_m / d) * (density * v * v / 2)) / 100000;
    }
}

class Simulator {
    constructor() {
        this.totalDepth = 3000;
        this.geology = Geology.generate(this.totalDepth);
        this.depth = 0;
        this.bitWear = 0;
        this.mudDensity = 1.20;
        this.wob = 10;
        this.rpm = 100;
        this.flowRate = 2000;
        this.budget = 10000000;
        this.stageIndex = 0;
        this.kickActive = false;
        this.pitVolume = 500;
        this.lastUpdate = Date.now();

        this.stages = [
            "Site Survey & Permitting", "Rig Mobilization", "Rig Up", "Conductor Drilling",
            "Conductor Casing & Cementing", "Nipple Up (Diverter)", "Surface Hole Drilling",
            "Surface Casing Running", "Surface Cementing", "Nipple Up (BOP)", "BOP Testing",
            "Intermediate I Hole Drilling", "Intermediate I Casing Running", "Intermediate I Cementing",
            "Intermediate II Hole Drilling", "Intermediate II Casing Running", "Intermediate II Cementing",
            "Production Hole Drilling", "Open Hole Logging", "Production Casing / Liner Running",
            "Production Cementing", "Well Completion", "Nipple Down BOP / Nipple Up Tree",
            "Perforation", "Stimulation", "Flowback & Testing", "Production Operations",
            "Workover / Intervention", "Enhanced Oil Recovery", "Plug & Abandonment (Temporary)",
            "Final Decommissioning"
        ];
    }

    getCurrentLayer() {
        return this.geology.find(l => this.depth >= l.top && this.depth <= l.bottom) || this.geology[this.geology.length - 1];
    }

    update() {
        let now = Date.now();
        let dt = (now - this.lastUpdate) / 1000;
        this.lastUpdate = now;
        let game_dt_hrs = dt / 60; // 1 real sec = 1 game min

        let layer = this.getCurrentLayer();
        let hydrostatic = (this.mudDensity * this.depth) / 10.197;
        let annLoss = Hydraulics.calculatePressureLoss(this.mudDensity, this.flowRate, 8.5, this.depth, 15, 12) * 0.3;
        let bhp = hydrostatic + annLoss;
        let ecd = (bhp * 10.197) / (this.depth || 1);

        // Drilling Logic
        if (this.flowRate > 500 && this.rpm > 0) {
            let clean_eff = Math.min(1.0, this.flowRate / 2500);
            let base_rop = (Math.pow(this.rpm, 0.7) * Math.pow(this.wob, 1.2)) / (layer.ucs * 0.5);
            let rop = base_rop * clean_eff * Math.exp(-2.0 * this.bitWear);
            this.depth += rop * game_dt_hrs;
            this.bitWear += (rop * layer.abrasivity * (layer.ucs / 50)) / 2000 * game_dt_hrs;
            this.rop = rop;
        } else {
            this.rop = 0;
        }

        // Safety
        let pore_p = (layer.pore_grad * this.depth) / 10;
        if (bhp < pore_p) {
            this.kickActive = true;
            let influx = (pore_p - bhp) * layer.permeability * 0.0001 * dt;
            this.pitVolume += influx;
        }

        // Economy
        this.budget -= (50000 / 24) * game_dt_hrs; // Daily rate

        return {
            depth: this.depth,
            rop: this.rop,
            bitWear: this.bitWear,
            ecd: ecd,
            bhp: bhp,
            kick: this.kickActive,
            pitVolume: this.pitVolume,
            stage: this.stages[this.stageIndex],
            budget: this.budget
        };
    }
}
