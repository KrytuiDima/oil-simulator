class Physics {
    static GRAVITY = 9.80665;

    // Bingham Plastic Pressure Loss (Pa)
    static calculatePressureLoss(rho, flow, d_id, length, pv, yp) {
        if (length <= 0 || d_id <= 0 || flow <= 0) return 0;
        const v = (flow / 60000) / (Math.PI * Math.pow(d_id / 2, 2));
        const gamma_dot = 8 * v / d_id;
        const mu_eff = (pv * 0.001) + (yp * 0.4788 / gamma_dot);
        const re = (rho * v * d_id) / mu_eff;
        const f = (re < 2100) ? (64 / re) : (0.3164 / Math.pow(re, 0.25));
        return f * (length / d_id) * (rho * v * v / 2);
    }

    static calculateMSE(wob_n, rpm, torque_nm, rop_ms, bit_d_m) {
        const area = Math.PI * Math.pow(bit_d_m / 2, 2);
        if (rop_ms <= 0) return 0;
        return (wob_n / area) + (2 * Math.PI * (rpm / 60) * torque_nm) / (area * rop_ms);
    }
}

class Geology {
    static LITHOLOGIES = {
        "Пісок": { ucs: [15, 40], por: [20, 35], perm: [200, 3000], abr: 0.3, color: "#fef08a" },
        "Глина": { ucs: [5, 25], por: [10, 20], perm: [0.001, 0.1], abr: 0.1, color: "#94a3b8" },
        "Вапняк": { ucs: [50, 150], por: [5, 20], perm: [1, 200], abr: 0.5, color: "#f8fafc" },
        "Доломіт": { ucs: [80, 220], por: [2, 15], perm: [0.1, 50], abr: 0.7, color: "#cbd5e1" },
        "Граніт": { ucs: [150, 350], por: [0.5, 2], perm: [0.0001, 0.01], abr: 0.9, color: "#fca5a5" }
    };

    static generate(totalDepth) {
        let layers = [];
        let curr = 0;
        while (curr < totalDepth) {
            const types = Object.keys(this.LITHOLOGIES);
            const name = types[Math.floor(Math.random() * types.length)];
            const props = this.LITHOLOGIES[name];
            const thick = 100 + Math.random() * 400;
            const bottom = Math.min(curr + thick, totalDepth);

            layers.push({
                name, top: curr, bottom, ...props,
                ucs: props.ucs[0] + Math.random() * (props.ucs[1] - props.ucs[0]),
                youngModulus: 10 + Math.random() * 40, // GPa
                poissonRatio: 0.2 + Math.random() * 0.15,
                mineralogy: { quartz: Math.random(), clay: Math.random() },
                fractures: Math.random() * 0.2,
                saturation: { oil: Math.random() * 0.3, gas: Math.random() * 0.2, water: 0.5 },
                pore_grad: 1.03 + (curr / 5000) * (0.1 + Math.random() * 0.6),
                frac_grad: 1.6 + (curr / 5000) * 0.4
            });
            curr = bottom;
        }
        return layers;
    }
}

class Simulator {
    constructor() {
        this.geology = Geology.generate(4000);
        this.depth = 0;
        this.targetDepth = 4000;
        this.wob = 0; this.rpm = 0; this.flow = 0; this.mudDensity = 1.10;
        this.pv = 15; this.yp = 12;
        this.bitWear = 0; this.bitImpactDamage = 0; this.pumpWear = 0;
        this.fuel = 100000; this.budget = 5000000;
        this.dailyRate = 85000; this.fuelPrice = 1.5;
        this.totalSpent = 0;
        this.stageIndex = 0;
        this.activeKick = false; this.pitVolume = 400;

        this.stages = [
            "Вибір ділянки", "Мобілізація", "Монтаж вишки", "Буріння під напрямну", "Спуск напрямної",
            "Цементування напрямної", "Монтаж дивертора", "Буріння під кондуктор", "Спуск кондуктора",
            "Цементування кондуктора", "Монтаж ПВО", "Випробування ПВО", "Буріння тех. секції 1",
            "Спуск тех. колони 1", "Цементування тех. 1", "Буріння тех. секції 2", "Спуск тех. колони 2",
            "Цементування тех. 2", "Буріння експлуатаційної секції", "ГІС в похилій свердловині",
            "Спуск експлуатаційної колони", "Цементування", "Вторинне розкриття", "Освоєння",
            "Стимуляція пласта", "Випробування пласта", "Видобуток", "КРС / ПРС",
            "Підтримання тиску", "Ліквідація", "Рекультивація"
        ].map((n, i) => ({ name: n, target: (i + 1) * 129, task: "Виконуйте роботи згідно плану" }));

        this.lastTime = Date.now();
        this.history = [];
    }

    update() {
        const now = Date.now();
        const dt_sec = (now - this.lastTime) / 1000;
        this.lastTime = now;
        const game_dt_min = dt_sec * 5;
        const game_dt_hr = game_dt_min / 60;

        const layer = this.geology.find(l => this.depth >= l.top && this.depth <= l.bottom) || this.geology[this.geology.length-1];

        const hydro = (this.mudDensity * this.depth) / 10.197;
        const annLoss = Physics.calculatePressureLoss(this.mudDensity*1000, this.flow, 0.08, this.depth, this.pv, this.yp) / 100000;
        this.bhp = hydro + (this.flow > 0 ? annLoss : 0);
        this.ecd = (this.bhp * 10.197) / (this.depth || 1);

        let rop = 0;
        if (this.flow > 500 && this.rpm > 10 && this.wob > 1) {
            const clean_eff = Math.min(1.0, this.flow / (this.depth * 0.5 + 1000));
            const wear_factor = Math.exp(-3 * this.bitWear);
            rop = (Math.pow(this.rpm, 0.6) * Math.pow(this.wob, 1.1) * 5) / (layer.ucs * 0.5);
            rop *= (clean_eff * wear_factor);

            this.depth += rop * game_dt_hr;
            this.bitWear += (rop * layer.abr * (layer.ucs / 100)) / 10000 * game_dt_min;
        }
        this.rop = rop;
        this.torque = 0.5 * this.wob * 0.2 * 0.3 * (layer.ucs / 50) + (this.rpm / 200);
        this.mse = Physics.calculateMSE(this.wob * 9806, this.rpm, this.torque * 1000, rop / 3600, 0.2159) / 1e6;

        const poreP = (layer.pore_grad * this.depth) / 10;
        this.activeKick = (this.bhp < poreP && this.depth > 100);
        if (this.activeKick) this.pitVolume += (poreP - this.bhp) * 0.001 * game_dt_min;

        const fuelBurn = (this.flow * 0.2) + (this.rpm * 0.5) + (this.wob * 0.1);
        const stepCost = (this.dailyRate / 24) * game_dt_hr + (fuelBurn * game_dt_hr * this.fuelPrice);
        this.budget -= stepCost;
        this.totalSpent += stepCost;
        this.fuel -= fuelBurn * game_dt_hr;

        return {
            depth: this.depth, rop: this.rop, bhp: this.bhp, ecd: this.ecd, mse: this.mse,
            bitWear: this.bitWear, budget: this.budget, fuel: this.fuel, kick: this.activeKick,
            pit: this.pitVolume, stage: this.stages[this.stageIndex], layer: layer, torque: this.torque
        };
    }

    getAIAdvice(res) {
        const advices = [];
        if (res.mse > res.layer.ucs * 3) advices.push(`AI: Енергія руйнування (MSE: ${res.mse.toFixed(0)}) занадто висока. Виникають вібрації. Зменште WOB.`);
        if (res.bitWear > 0.7) advices.push("AI: Високий знос долота. Ефективність буріння падає експоненціально.");
        if (res.kick) advices.push("AI: ТЕРМІНОВО! Пластовий тиск перевищив тиск у свердловині. Закрийте ПВО та важіть розчин!");
        if (res.rop < 2 && res.rpm > 100) advices.push("AI: Полірування вибою. Недостатнє навантаження для поточної твердості породи.");
        return advices.length > 0 ? advices : ["AI: Параметри в нормі. Продовжуйте буріння."];
    }
}
