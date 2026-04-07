"""
quantum_engine.py
Core quantum circuit logic using Qiskit.
Handles state initialization, gate application, and statevector simulation.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix
from qiskit.circuit.library import (
    HGate, XGate, YGate, ZGate, SGate, TGate, SdgGate, TdgGate,
    RXGate, RYGate, RZGate, IGate, CXGate, CZGate, CYGate,
    SwapGate, CHGate, CRXGate, CRYGate, CRZGate, ECRGate
)
from typing import Optional, List, Dict, Tuple
import warnings
warnings.filterwarnings("ignore")


# ─── Gate Catalogue ───────────────────────────────────────────────────────────

SINGLE_QUBIT_GATES: Dict[str, Dict] = {
    "H":   {"name": "Hadamard",    "symbol": "H",   "params": [],      "color": "#00d4ff",
            "desc": "Creates equal superposition: |0⟩ → (|0⟩+|1⟩)/√2"},
    "X":   {"name": "Pauli-X",     "symbol": "X",   "params": [],      "color": "#ff6b6b",
            "desc": "Bit-flip gate: |0⟩ ↔ |1⟩ (quantum NOT)"},
    "Y":   {"name": "Pauli-Y",     "symbol": "Y",   "params": [],      "color": "#ffa94d",
            "desc": "Combines bit and phase flip: |0⟩ → i|1⟩, |1⟩ → -i|0⟩"},
    "Z":   {"name": "Pauli-Z",     "symbol": "Z",   "params": [],      "color": "#a9e34b",
            "desc": "Phase-flip gate: |1⟩ → -|1⟩, |0⟩ unchanged"},
    "S":   {"name": "S Gate",      "symbol": "S",   "params": [],      "color": "#74c0fc",
            "desc": "√Z gate: adds π/2 phase to |1⟩"},
    "T":   {"name": "T Gate",      "symbol": "T",   "params": [],      "color": "#b197fc",
            "desc": "√S gate: adds π/4 phase to |1⟩"},
    "Sdg": {"name": "S†",          "symbol": "S†",  "params": [],      "color": "#74c0fc",
            "desc": "Inverse S gate: subtracts π/2 phase"},
    "Tdg": {"name": "T†",          "symbol": "T†",  "params": [],      "color": "#b197fc",
            "desc": "Inverse T gate: subtracts π/4 phase"},
    "RX":  {"name": "Rx(θ)",       "symbol": "Rx",  "params": ["θ"],   "color": "#ff8787",
            "desc": "Rotation around X-axis by angle θ"},
    "RY":  {"name": "Ry(θ)",       "symbol": "Ry",  "params": ["θ"],   "color": "#ffa94d",
            "desc": "Rotation around Y-axis by angle θ"},
    "RZ":  {"name": "Rz(θ)",       "symbol": "Rz",  "params": ["θ"],   "color": "#a9e34b",
            "desc": "Rotation around Z-axis by angle θ"},
    "I":   {"name": "Identity",    "symbol": "I",   "params": [],      "color": "#868e96",
            "desc": "Identity gate: no operation"},
}

TWO_QUBIT_GATES: Dict[str, Dict] = {
    "CNOT": {"name": "CNOT",       "symbol": "CX",  "params": [],      "color": "#00d4ff",
             "desc": "Controlled-NOT: flips target if control is |1⟩"},
    "CZ":   {"name": "CZ",         "symbol": "CZ",  "params": [],      "color": "#74c0fc",
             "desc": "Controlled-Z: applies Z to target if control is |1⟩"},
    "CY":   {"name": "CY",         "symbol": "CY",  "params": [],      "color": "#ffa94d",
             "desc": "Controlled-Y: applies Y to target if control is |1⟩"},
    "SWAP": {"name": "SWAP",       "symbol": "SW",  "params": [],      "color": "#b197fc",
             "desc": "Exchanges states of two qubits"},
    "CH":   {"name": "CH",         "symbol": "CH",  "params": [],      "color": "#a9e34b",
             "desc": "Controlled-Hadamard: applies H to target if control is |1⟩"},
    "CRX":  {"name": "CRx(θ)",     "symbol": "CRx", "params": ["θ"],   "color": "#ff8787",
             "desc": "Controlled Rx rotation by θ"},
    "CRY":  {"name": "CRy(θ)",     "symbol": "CRy", "params": ["θ"],   "color": "#ffa94d",
             "desc": "Controlled Ry rotation by θ"},
    "CRZ":  {"name": "CRz(θ)",     "symbol": "CRz", "params": ["θ"],   "color": "#a9e34b",
             "desc": "Controlled Rz rotation by θ"},
}


def normalize_state(amplitudes: np.ndarray) -> np.ndarray:
    """Normalize a complex amplitude array to unit norm."""
    norm = np.linalg.norm(amplitudes)
    if norm < 1e-12:
        raise ValueError("Zero-norm state vector.")
    return amplitudes / norm


def build_initial_statevector(n_qubits: int,
                               values: np.ndarray,
                               val_min: float,
                               val_max: float) -> np.ndarray:
    """
    Build a normalized statevector from user-supplied raw values.
    - values: array of length 2^n_qubits (real or complex)
    - Clamps to [val_min, val_max], then normalizes.
    """
    dim = 2 ** n_qubits
    if len(values) != dim:
        raise ValueError(f"Need {dim} amplitudes for {n_qubits} qubits.")
    clipped = np.clip(np.abs(values), val_min, val_max)
    phases = np.angle(values)
    reconstructed = clipped * np.exp(1j * phases)
    return normalize_state(reconstructed)


class QuantumCircuitSession:
    """
    Maintains the full circuit state across interactive steps.
    """

    def __init__(self, n_qubits: int, init_statevector: np.ndarray):
        self.n_qubits = n_qubits
        self.init_sv = Statevector(normalize_state(init_statevector))
        self.circuit = QuantumCircuit(n_qubits)
        self.history: List[Dict] = []  # log of applied gates
        self._current_sv: Statevector = self.init_sv

    # ── Current state ──────────────────────────────────────────────────────
    @property
    def statevector(self) -> Statevector:
        return self._current_sv

    @property
    def probabilities(self) -> np.ndarray:
        return self._current_sv.probabilities()

    @property
    def num_gates(self) -> int:
        return len(self.history)

    # ── Gate application ───────────────────────────────────────────────────
    def apply_single_qubit_gate(self, gate_key: str, qubit: int,
                                 param: Optional[float] = None) -> Dict:
        """Apply a single-qubit gate and return a result dict."""
        self._validate_qubit(qubit)
        info = SINGLE_QUBIT_GATES[gate_key]

        gate_obj = self._build_single_gate(gate_key, param)
        self.circuit.append(gate_obj, [qubit])

        old_sv = self._current_sv
        self._current_sv = self._current_sv.evolve(gate_obj, [qubit])

        return self._make_record("single", gate_key, info, [qubit], param, old_sv)

    def apply_two_qubit_gate(self, gate_key: str, control: int, target: int,
                              param: Optional[float] = None) -> Dict:
        """Apply a two-qubit gate and return a result dict."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise ValueError("Control and target must differ.")
        info = TWO_QUBIT_GATES[gate_key]

        gate_obj = self._build_two_gate(gate_key, param)
        self.circuit.append(gate_obj, [control, target])

        old_sv = self._current_sv
        self._current_sv = self._current_sv.evolve(gate_obj, [control, target])

        return self._make_record("two", gate_key, info, [control, target], param, old_sv)

    # ── Internals ──────────────────────────────────────────────────────────
    def _build_single_gate(self, key: str, param):
        map_ = {
            "H": HGate(), "X": XGate(), "Y": YGate(), "Z": ZGate(),
            "S": SGate(), "T": TGate(), "Sdg": SdgGate(), "Tdg": TdgGate(),
            "I": IGate(),
            "RX": RXGate(param or 0.0),
            "RY": RYGate(param or 0.0),
            "RZ": RZGate(param or 0.0),
        }
        return map_[key]

    def _build_two_gate(self, key: str, param):
        map_ = {
            "CNOT": CXGate(), "CZ": CZGate(), "CY": CYGate(),
            "SWAP": SwapGate(), "CH": CHGate(),
            "CRX": CRXGate(param or 0.0),
            "CRY": CRYGate(param or 0.0),
            "CRZ": CRZGate(param or 0.0),
        }
        return map_[key]

    def _validate_qubit(self, q: int):
        if not (0 <= q < self.n_qubits):
            raise ValueError(f"Qubit index {q} out of range [0, {self.n_qubits-1}].")

    def _make_record(self, kind, key, info, qubits, param, old_sv) -> Dict:
        new_probs = self._current_sv.probabilities()
        old_probs = old_sv.probabilities()
        delta_entropy = self._entropy(new_probs) - self._entropy(old_probs)

        label = info["symbol"]
        if param is not None:
            label += f"({param:.3f})"

        record = {
            "step": len(self.history) + 1,
            "kind": kind,
            "gate_key": key,
            "gate_name": info["name"],
            "gate_label": label,
            "qubits": qubits,
            "param": param,
            "description": info["desc"],
            "color": info["color"],
            "statevector": self._current_sv.data.copy(),
            "probabilities": new_probs,
            "delta_entropy": delta_entropy,
        }
        self.history.append(record)
        return record

    @staticmethod
    def _entropy(probs: np.ndarray) -> float:
        p = probs[probs > 1e-12]
        return float(-np.sum(p * np.log2(p)))

    def get_circuit_ascii(self) -> str:
        return str(self.circuit.draw(output="text", fold=-1))

    def get_basis_labels(self) -> List[str]:
        n = self.n_qubits
        return [f"|{format(i, f'0{n}b')}⟩" for i in range(2 ** n)]

    def bloch_data_for_qubit(self, q: int) -> Tuple[float, float, float]:
        """Return (x,y,z) Bloch vector for qubit q via reduced density matrix."""
        from qiskit.quantum_info import partial_trace
        dm_full = DensityMatrix(self._current_sv)
        # Trace out all qubits except q
        qubits_to_trace = [i for i in range(self.n_qubits) if i != q]
        if qubits_to_trace:
            rho_q = partial_trace(dm_full, qubits_to_trace)
        else:
            rho_q = dm_full
        rho = rho_q.data
        x = 2 * np.real(rho[0, 1])
        y = 2 * np.imag(rho[1, 0])
        z = np.real(rho[0, 0] - rho[1, 1])
        return float(x), float(y), float(z)
