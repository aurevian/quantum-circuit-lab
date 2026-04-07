# Contributing to Quantum Circuit Lab

Thank you for your interest in contributing. This document covers how to set up a development environment, add gates, and submit changes.

---

## Development Setup

```bash
git clone https://github.com/<your-username>/quantum-circuit-lab.git
cd quantum-circuit-lab

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
```

Run the app locally:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest tests/ -v
pytest tests/ -v --cov=quantum_engine   # with coverage
```

---

## Project Structure

```
quantum-circuit-lab/
├── app.py               # Streamlit UI — 3 stages: setup → build → results
├── quantum_engine.py    # Core Qiskit logic: gates, session, statevector
├── visualizer.py        # Plotly visualizations: histogram, Bloch, entropy
├── tests/
│   └── test_quantum_engine.py
├── .github/
│   └── workflows/ci.yml
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Adding a New Gate

### Single-qubit gate

**Step 1** — Register in `quantum_engine.py → SINGLE_QUBIT_GATES`:

```python
"MY_GATE": {
    "name":   "My Gate",
    "symbol": "MG",
    "params": [],          # [] for fixed, ["θ"] for parametric
    "color":  "#ff6b6b",
    "desc":   "What this gate does to the qubit state",
},
```

**Step 2** — Implement in `_build_single_gate()`:

```python
"MY_GATE": MyGateFromQiskit(),
```

**Step 3** — If parametric, add scale name in `app.py → SCALE_NAMES`:

```python
"MY_GATE": "α_mg",
```

**Step 4** — Add to `PARAMETRIC_SINGLE` if it takes an angle parameter.

**Step 5** — Write a test in `tests/test_quantum_engine.py`.

### Two-qubit gate

Same pattern using `TWO_QUBIT_GATES`, `_build_two_gate()`, and `PARAMETRIC_TWO`.

> **Rule**: Three-or-more qubit gates (Toffoli, Fredkin, etc.) are intentionally excluded from the interface to keep the UX focused. Decompose into 1- and 2-qubit gates if needed.

---

## Gate Scale System

Parametric gates use the formula: **θ = α × x_i × π**

- `α` (gate scale) is entered once per gate type and remembered until circuit reset.
- `x_i` (data value) is entered each time the gate is applied.

This design supports encoding classical dataset values as rotation angles, which is the standard approach in variational quantum circuits and QML.

---

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR.
- All tests must pass (`pytest tests/ -v`).
- New gates must include at least one unit test.
- Update `README.md` if adding a user-facing feature.
- Use descriptive commit messages: `feat: add Ising ZZ gate`, `fix: normalize edge case`.

---

## Reporting Issues

Open a GitHub Issue with:
- Python version and OS
- Qiskit version (`python -c "import qiskit; print(qiskit.__version__)"`)
- Steps to reproduce
- Expected vs actual behaviour
