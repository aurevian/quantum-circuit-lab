<div align="center">

# ⚛ Quantum Circuit Lab

**An interactive, Qiskit-powered quantum circuit builder with real-time statevector simulation**

*Built for researchers and practitioners who want to build, visualise, and understand quantum circuits — interactively.*

[![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.x-6929C4?style=flat-square&logo=qiskit&logoColor=white)](https://qiskit.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/<YOUR-USERNAME>/quantum-circuit-lab/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/<YOUR-USERNAME>/quantum-circuit-lab/actions)

<br/>

*by* ***Eren Bozkurt***  
*PhD Researcher in Quantum Computing · Loughborough University*

</div>

---

## Overview

Quantum Circuit Lab is a browser-based interactive application for constructing and simulating quantum circuits step by step. At each stage it shows the circuit diagram, the full statevector, measurement probabilities, Bloch sphere representations, and an entropy timeline — all updated in real time after every gate application.

The tool is designed with variational quantum circuit workflows in mind. Parametric gates follow the formula **θ = α × x_i × π**, where α is a learnable scale factor and x_i is a data-point input — the standard encoding pattern in quantum machine learning.

---

## Features

### Interactive Circuit Construction
- **1 to 6 qubits** — state space up to 64 dimensions
- **Custom initial states** — enter arbitrary complex amplitudes; validated against a user-defined [min, max] range, then automatically normalized
- **Step-by-step gate application** — select a gate, configure it, apply, observe the effect immediately

### Gate Catalogue

| Category | Gates |
|---|---|
| **Single-qubit** | H, X, Y, Z, S, T, S†, T†, I, Rx(θ), Ry(θ), Rz(θ) |
| **Two-qubit** | CNOT, CZ, CY, SWAP, CH, CRx(θ), CRy(θ), CRz(θ) |

> Three-or-more qubit gates (Toffoli, Fredkin) are intentionally excluded — they decompose into 1- and 2-qubit gates and their inclusion would obscure the learning process.

### Parametric Gate Scale System
Rotation gates (Rx, Ry, Rz, CRx, CRy, CRz) use the encoding:

```
θ = α_gate × x_i × π
```

- **α_gate** (gate scale) — entered once per gate type, stored in memory until the circuit is reset. Provides a per-parameter learnable scale analogous to VQC weight initialisation.
- **x_i** (data value) — entered at each gate application. Represents a feature value from a dataset, enabling classical-to-quantum encoding directly in the interface.

The computed angle is shown live: `θ = 0.5000 × 0.3000 × π = 0.47124 rad (27.00°)`.

### Visualisations

| Panel | Description |
|---|---|
| **Circuit Diagram** | ASCII circuit drawn by Qiskit after each gate |
| **Probability Histogram** | Measurement probability per basis state |
| **Statevector Table** | Full amplitude table: Re(ψ), Im(ψ), \|ψ\|, probability |
| **Amplitude Chart** | Grouped bar chart of real/imaginary parts + magnitude |
| **Bloch Sphere** | Per-qubit Bloch vector via partial trace of the density matrix |
| **Entropy Timeline** | von Neumann entropy S = −∑ pᵢ log₂(pᵢ) after every gate |
| **Operation History** | Annotated gate log with entropy delta, α, x_i, θ per step |

### Final Report
After finalising the circuit, a complete report is generated:
- Full annotated circuit diagram
- Final statevector with all amplitudes
- Measurement probability distribution
- Bloch spheres for all qubits
- Complete gate history with entropy deltas
- Entropy evolution plot

---

## Installation

### Prerequisites

- Python 3.10, 3.11, or 3.12
- pip

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/<YOUR-USERNAME>/quantum-circuit-lab.git
cd quantum-circuit-lab

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Usage

### Stage 1 — Setup

1. Set the number of qubits (1–6).
2. Set the amplitude min/max range. All input magnitudes must fall within this range.
3. Enter the initial state amplitudes as space- or comma-separated real or complex numbers.
   - Real: `1 0 0 0`
   - Complex: `0.5+0.5j, 0.5-0.5j, 0, 0`
4. Use quick-preset buttons for |0…0⟩, equal superposition, or |1…1⟩.
5. Click **Initialize Circuit**.

### Stage 2 — Build

Use the sidebar to:

1. Choose **Single Qubit** or **Two Qubit** gate category.
2. Select the target qubit (and control qubit for 2-qubit gates).
3. Click a gate button to select it.
4. **Parametric gates only**: set the gate scale α (first use) and enter x_i (every use). The computed angle is shown before applying.
5. Click **Apply Gate**. All visualisation panels update immediately.
6. Repeat. Click **Finalize Circuit** when done.

### Stage 3 — Final Results

A full summary report is displayed. Navigate back to the builder or reset to start a new circuit.

---

## Architecture

```
quantum-circuit-lab/
├── app.py                     # Streamlit UI — 3-stage workflow
├── quantum_engine.py          # Qiskit engine: gate catalogue, QuantumCircuitSession
├── visualizer.py              # Plotly charts: histogram, Bloch sphere, entropy
├── tests/
│   └── test_quantum_engine.py # 27 unit tests
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI (Python 3.10, 3.11, 3.12)
├── .streamlit/
│   └── config.toml            # Dark theme configuration
├── requirements.txt
├── requirements-dev.txt
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

### Key Design Decisions

**Exact statevector simulation.**  
Uses `qiskit.quantum_info.Statevector.evolve()` — no shot sampling, no approximation. Every probability is exact.

**Bloch vectors from partial trace.**  
For n-qubit systems, the single-qubit Bloch vector for qubit q is computed by tracing out all other qubits from the density matrix, giving the correct reduced state even under entanglement.

**Amplitude validation, not clipping.**  
User inputs are checked against [min, max] and rejected with a clear error if out of range. This preserves the intended state and avoids silent data corruption.

**Gate scale memory.**  
α values are stored in Streamlit session state and survive stage transitions. They are cleared only on a full reset, matching the expected workflow where a researcher applies the same gate with different x_i values across many steps.

---

## Extending the Gate Catalogue

### Add a new single-qubit gate

**`quantum_engine.py`** — register in `SINGLE_QUBIT_GATES`:

```python
"MY_GATE": {
    "name":   "My Gate",
    "symbol": "MG",
    "params": [],        # ["θ"] if parametric
    "color":  "#ff6b6b",
    "desc":   "Description of what this gate does",
},
```

Add to `_build_single_gate()`:

```python
"MY_GATE": MyGate(),
```

**`app.py`** — if parametric, add to `PARAMETRIC_SINGLE` and `SCALE_NAMES`:

```python
PARAMETRIC_SINGLE = {"RX", "RY", "RZ", "MY_GATE"}
SCALE_NAMES = { ..., "MY_GATE": "α_mg" }
```

Add a test in `tests/test_quantum_engine.py`.

### Add a new two-qubit gate

Same pattern with `TWO_QUBIT_GATES`, `_build_two_gate()`, `PARAMETRIC_TWO`.

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=quantum_engine --cov-report=term-missing
```

Current test coverage: **27 tests** across normalization, gate correctness, Bell states, Bloch vectors, error handling, and catalogue integrity.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `qiskit` | ≥ 2.0 | Quantum circuit construction and exact simulation |
| `qiskit-aer` | ≥ 0.15 | Aer simulator backend (available for future shot-based simulation) |
| `streamlit` | ≥ 1.30 | Interactive web application framework |
| `plotly` | ≥ 5.18 | Interactive visualisations |
| `numpy` | ≥ 1.24 | Numerical operations |
| `matplotlib` | ≥ 3.7 | ASCII circuit diagram rendering (via Qiskit) |

---


## Citation

If you use this tool in a research context, you may cite it as:

```bibtex
@software{bozkurt2025qclab,
  author    = {Bozkurt, Eren},
  title     = {Quantum Circuit Lab: An Interactive Qiskit-Powered Circuit Builder},
  year      = {2025},
  url       = {https://github.com/<YOUR-USERNAME>/quantum-circuit-lab},
  license   = {MIT}
}
```

---

<div align="center">
<sub>Built with Qiskit · Streamlit · Plotly</sub>
</div>
