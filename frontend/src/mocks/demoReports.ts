/**
 * Demo-mode content. Used only when no backend is reachable, so the UI can be
 * explored without running Python.
 */

export interface DemoReport {
  report: string;
  stats: PipelineStatsLike;
}

interface PipelineStatsLike {
  total_pages: number;
  total_chunks: number;
  recent_pages?: number;
  avg_chunks_per_page: number;
}

export const DEMO_REPORTS: Record<string, DemoReport> = {
  "solid-state battery": {
    stats: { total_pages: 35, total_chunks: 172, recent_pages: 6, avg_chunks_per_page: 4.9 },
    report: `# Advanced Anode Materials and Dendrite Prevention in Solid-State Batteries

## 1. Executive Summary
Solid-state lithium batteries (SSLBs) offer superior energy density and safety compared to conventional liquid electrolyte cells. However, **lithium dendrite penetration** through solid electrolytes (SEs) remains a primary failure mechanism, causing internal short circuits and cell death. This study synthesizes mechanical, electrochemical, and metallurgical strategies to overcome dendrite propagation, focusing on state-of-the-art anode designs.

---

## 2. Technical Evaluation Matrix
Below is a structured analysis of solid electrolyte (SE) classes and their mechanical parameters impacting dendrite prevention:

| Solid Electrolyte Class | Shear Modulus (GPa) | Li-Ion Conductivity (mS/cm) | Primary Failure Vector | Dendrite Resistance |
| :--- | :---: | :---: | :--- | :---: |
| **Garnet-Type (LLZO)** | 61.2 | 1.0 - 2.5 | Grain boundary conduction | Medium |
| **Sulfide-Type (LPSCl)** | 18.5 | 3.0 - 12.0 | High electronic leakage | Low |
| **Polymer (PEO-LiTFSI)** | 0.12 | 0.01 - 0.1 | Elastic mechanical failure | Very Low |
| **Composite (LLZO-PVDF)** | 8.4 | 0.5 - 1.2 | Phase boundary resistance | High |

> **Key Takeaway:** While LLZO ceramic offers superior shear modulus, high lithium-metal interface roughness creates local electric-field hotspots that drive grain-boundary penetration.

---

## 3. Comparative Dendrite Prevention Methodologies

### A. Metallurgical Anode Surface Modification
Applying thin, lithiophilic interlayers mitigates high surface impedance between lithium metal and solid electrolytes:
* **Atomic Layer Deposition (ALD):** Depositing 2-5 nm of \`Al2O3\` or \`ZnO\`, which reacts with Li to form conductive alloy interfaces.
* **Chemical Vapor Deposition (CVD):** Infusing ultrathin carbonaceous layers to distribute local current density evenly.

### B. 3D Porous Lithiophilic Frameworks
Placing lithium inside sub-micron pore frameworks instead of planar foil eliminates local mechanical stress:
1. *In-situ* alloy scaffolding (\`Li-Mg\`, \`Li-In\`).
2. Nitrogen-doped carbon nanotube matrices providing superior electronic conduits.

---

## 4. Current Academic Recommendations
Researchers must shift design priorities from electrolyte thickness to **microstructural density control**. Sintering must reach \`> 98.5%\` relative theoretical density to bypass grain-boundary lithium tracking.
`,
  },
  "quantum computing": {
    stats: { total_pages: 58, total_chunks: 290, recent_pages: 11, avg_chunks_per_page: 5.0 },
    report: `# Next-Generation Quantum Computing Hardware: Superconducting vs Neutral Atom Qubits

## 1. Technological Abstract
The quantum computing industry is witnessing an intense rivalry between **superconducting Josephson-junction qubits** and **neutral atom (Rydberg) qubits**. This evaluation maps physical parameters, error-correction overheads, and fault-tolerant scaling for both paradigms.

---

## 2. Hardware Benchmark Matrix

| Physics Paradigm | Coherence Time | Single-Qubit Fidelity | Two-Qubit Fidelity | Operating Temp |
| :--- | :---: | :---: | :---: | :---: |
| **Superconducting** (Transmon) | ~100 µs | 99.99% | 99.8% | 15 mK |
| **Neutral Atoms** (Rubidium) | ~10 s | 99.95% | 99.5% | Room temp vacuum |
| **Ion Trap** (Ytterbium) | ~100 s | 99.99% | 99.9% | Room temp vacuum |
| **Silicon Spin Qubits** | ~10 ms | 99.9% | 99.0% | 1.1 K |

> **Analyst Consensus:** Neutral atom systems have rapidly scaled past 1,000 qubits thanks to optical-tweezer rearrangement, bypassing the wiring limits of dilution refrigerators.

---

## 3. Scalability and Error Mitigation Vectors

### A. Neutral Rydberg Atoms
* **Mechanism:** Rubidium or strontium atoms suspended in optical trap arrays; entanglement is switched on via Rydberg-state excitation.
* **Strength:** Atomically identical qubits, avoiding lithography-induced fabrication variance.

### B. Superconducting Transmon Chips
* **Mechanism:** Microsecond microwave pulse routing over coaxial feeds into niobium/aluminum loops.
* **Strength:** Extremely fast gates (~10 ns), enabling rapid error extraction under surface-code architectures.

---

## 4. Engineering Outlook
Superconducting chips remain dominant in commercial clouds, while neutral-atom platforms offer the shortest timeline to early fault-tolerant simulation workloads.
`,
  },
  "smr reactors": {
    stats: { total_pages: 42, total_chunks: 210, recent_pages: 8, avg_chunks_per_page: 5.0 },
    report: `# Coolant Efficiency and Thermal Benchmarks in Small Modular Nuclear Reactors (SMRs)

## 1. Executive Briefing
Small Modular Reactors present a decentralized, factory-fabricated alternative to gigawatt-scale fission plants. SMR safety margins rely on passive natural-convection coolant design; this study benchmarks heat-exchanger coefficients of advanced coolants.

---

## 2. Coolant Thermodynamic Specifications

| Coolant | Temp Range (°C) | Volumetric Heat Capacity (kJ/m³·K) | Pressure (MPa) | Safety Profile |
| :--- | :---: | :---: | :---: | :--- |
| **Superheated Light Water** | 280 - 325 | 3,100 | 15.0 | Negative void coefficient risk |
| **Liquid Sodium** | 390 - 540 | 1,120 | 0.1 | High chemical reactivity |
| **Molten FLiBe Salt** | 550 - 700 | 4,200 | 0.1 | Excellent (passive) |
| **Helium Gas** | 450 - 850 | 5.4 | 7.0 | Single-phase stability |

> **Safety Note:** High pressure in light-water SMRs demands heavy containment structures; molten-salt designs run at atmospheric pressure, virtually eliminating rupture threats.

---

## 3. Passive Safety Mechanics
Advanced SMRs prevent core damage *without operator intervention*:
1. **Buoyancy-driven convection:** heated coolant rises into auxiliary condensers without pumps.
2. **Freeze-plug drains:** molten-salt reactors use actively cooled plugs that melt on power loss, draining fuel into sub-critical dump tanks.
`,
  },
};

export function pickDemoReport(query: string): DemoReport {
  const lower = query.toLowerCase();
  if (lower.includes("quantum")) return DEMO_REPORTS["quantum computing"];
  if (lower.includes("smr") || lower.includes("reactor") || lower.includes("nuclear"))
    return DEMO_REPORTS["smr reactors"];
  if (lower.includes("battery") || lower.includes("solid")) return DEMO_REPORTS["solid-state battery"];
  return DEMO_REPORTS["solid-state battery"];
}

export const DEMO_STAGES: Array<{ stage: string; output: string }> = [
  { stage: "Planner", output: "Expanded query into 5 focused keyword clusters." },
  { stage: "Scraper", output: "Crawled 25 technical articles; removed boilerplate & paywalls." },
  { stage: "Analyzer", output: "Generated 120 vector embeddings with semantic deduplication." },
  { stage: "Writer", output: "Synthesized comprehensive markdown chapters with cross-reference tables." },
  { stage: "Critic", output: "Critic consensus rating: 9.4/10 - passed factual consistency check." },
];
