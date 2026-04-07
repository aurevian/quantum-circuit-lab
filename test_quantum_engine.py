"""
tests/test_quantum_engine.py
Unit tests for the Quantum Circuit Lab engine.
"""

import numpy as np
import pytest
from quantum_engine import (
    QuantumCircuitSession,
    SINGLE_QUBIT_GATES,
    TWO_QUBIT_GATES,
    normalize_state,
    build_initial_statevector,
)

# Parametric gate sets (mirrored from app.py for test assertions)
PARAMETRIC_SINGLE = {"RX", "RY", "RZ"}
PARAMETRIC_TWO    = {"CRX", "CRY", "CRZ"}

# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def ground_state_1q():
    sv = normalize_state(np.array([1, 0], dtype=complex))
    return QuantumCircuitSession(1, sv)

@pytest.fixture
def ground_state_2q():
    sv = normalize_state(np.array([1, 0, 0, 0], dtype=complex))
    return QuantumCircuitSession(2, sv)

@pytest.fixture
def equal_super_2q():
    sv = normalize_state(np.ones(4, dtype=complex))
    return QuantumCircuitSession(2, sv)


# ─── normalize_state ──────────────────────────────────────────────────────────

def test_normalize_already_unit():
    v = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
    out = normalize_state(v)
    assert abs(np.linalg.norm(out) - 1.0) < 1e-10

def test_normalize_scales_correctly():
    v = np.array([3.0, 4.0], dtype=complex)
    out = normalize_state(v)
    assert abs(np.linalg.norm(out) - 1.0) < 1e-10
    assert abs(float(np.real(out[0])) - 0.6) < 1e-10

def test_normalize_zero_raises():
    with pytest.raises(ValueError, match="Zero-norm"):
        normalize_state(np.array([0, 0], dtype=complex))


# ─── build_initial_statevector ────────────────────────────────────────────────

def test_build_sv_wrong_length():
    with pytest.raises(ValueError, match="2 qubits"):
        build_initial_statevector(2, np.array([1, 0, 0], dtype=complex), 0.0, 1.0)

def test_build_sv_normalizes():
    sv = build_initial_statevector(1, np.array([3.0, 4.0], dtype=complex), 0.0, 5.0)
    assert abs(np.linalg.norm(sv) - 1.0) < 1e-10

def test_build_sv_clips_magnitude():
    # magnitude 2.0, max=1.0 → clipped to 1.0 then normalized
    sv = build_initial_statevector(1, np.array([2.0, 0], dtype=complex), 0.0, 1.0)
    assert abs(sv[0] - 1.0) < 1e-10


# ─── QuantumCircuitSession ────────────────────────────────────────────────────

def test_initial_probabilities_ground(ground_state_1q):
    probs = ground_state_1q.probabilities
    assert abs(probs[0] - 1.0) < 1e-10
    assert abs(probs[1] - 0.0) < 1e-10

def test_hadamard_creates_superposition(ground_state_1q):
    ground_state_1q.apply_single_qubit_gate("H", 0)
    probs = ground_state_1q.probabilities
    assert abs(probs[0] - 0.5) < 1e-8
    assert abs(probs[1] - 0.5) < 1e-8

def test_pauli_x_flips_state(ground_state_1q):
    ground_state_1q.apply_single_qubit_gate("X", 0)
    probs = ground_state_1q.probabilities
    assert abs(probs[0] - 0.0) < 1e-10
    assert abs(probs[1] - 1.0) < 1e-10

def test_pauli_x_twice_is_identity(ground_state_1q):
    ground_state_1q.apply_single_qubit_gate("X", 0)
    ground_state_1q.apply_single_qubit_gate("X", 0)
    probs = ground_state_1q.probabilities
    assert abs(probs[0] - 1.0) < 1e-10

def test_pauli_z_doesnt_change_probs(ground_state_1q):
    probs_before = ground_state_1q.probabilities.copy()
    ground_state_1q.apply_single_qubit_gate("Z", 0)
    probs_after = ground_state_1q.probabilities
    np.testing.assert_allclose(probs_before, probs_after, atol=1e-10)

def test_bell_state_probabilities(ground_state_2q):
    ground_state_2q.apply_single_qubit_gate("H", 0)
    ground_state_2q.apply_two_qubit_gate("CNOT", 0, 1)
    probs = ground_state_2q.probabilities
    assert abs(probs[0] - 0.5) < 1e-8   # |00>
    assert abs(probs[3] - 0.5) < 1e-8   # |11>
    assert abs(probs[1]) < 1e-10         # |01>
    assert abs(probs[2]) < 1e-10         # |10>

def test_gate_count_increments(ground_state_2q):
    assert ground_state_2q.num_gates == 0
    ground_state_2q.apply_single_qubit_gate("H", 0)
    assert ground_state_2q.num_gates == 1
    ground_state_2q.apply_two_qubit_gate("CNOT", 0, 1)
    assert ground_state_2q.num_gates == 2

def test_history_record_structure(ground_state_1q):
    record = ground_state_1q.apply_single_qubit_gate("H", 0)
    assert "step" in record
    assert "gate_key" in record
    assert "probabilities" in record
    assert "description" in record
    assert "delta_entropy" in record
    assert record["step"] == 1
    assert record["gate_key"] == "H"

def test_rotation_gate_rx(ground_state_1q):
    # RX(π) should flip |0> → |1>
    ground_state_1q.apply_single_qubit_gate("RX", 0, param=np.pi)
    probs = ground_state_1q.probabilities
    assert abs(probs[1] - 1.0) < 1e-6

def test_rotation_gate_ry_half_pi(ground_state_1q):
    # RY(π/2) should create equal superposition
    ground_state_1q.apply_single_qubit_gate("RY", 0, param=np.pi / 2)
    probs = ground_state_1q.probabilities
    assert abs(probs[0] - 0.5) < 1e-6
    assert abs(probs[1] - 0.5) < 1e-6

def test_scale_formula(ground_state_1q):
    # θ = alpha * xi * pi; alpha=1, xi=0.5 => pi/2 => equal super
    alpha, xi = 1.0, 0.5
    theta = alpha * xi * np.pi
    ground_state_1q.apply_single_qubit_gate("RY", 0, param=theta)
    probs = ground_state_1q.probabilities
    assert abs(probs[0] - 0.5) < 1e-6
    assert abs(probs[1] - 0.5) < 1e-6

def test_invalid_qubit_raises(ground_state_1q):
    with pytest.raises(ValueError):
        ground_state_1q.apply_single_qubit_gate("H", 5)

def test_same_control_target_raises(ground_state_2q):
    with pytest.raises(ValueError, match="differ"):
        ground_state_2q.apply_two_qubit_gate("CNOT", 0, 0)

def test_probabilities_sum_to_one(ground_state_2q):
    ground_state_2q.apply_single_qubit_gate("H", 0)
    ground_state_2q.apply_single_qubit_gate("H", 1)
    probs = ground_state_2q.probabilities
    assert abs(np.sum(probs) - 1.0) < 1e-10

def test_bloch_vector_ground_state(ground_state_1q):
    x, y, z = ground_state_1q.bloch_data_for_qubit(0)
    assert abs(x) < 1e-6
    assert abs(y) < 1e-6
    assert abs(z - 1.0) < 1e-6   # |0> → north pole

def test_bloch_vector_excited_state(ground_state_1q):
    ground_state_1q.apply_single_qubit_gate("X", 0)
    x, y, z = ground_state_1q.bloch_data_for_qubit(0)
    assert abs(x) < 1e-6
    assert abs(y) < 1e-6
    assert abs(z + 1.0) < 1e-6   # |1> → south pole

def test_basis_labels_2q(ground_state_2q):
    labels = ground_state_2q.get_basis_labels()
    assert labels == ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]

def test_statevector_norm_preserved(ground_state_2q):
    ground_state_2q.apply_single_qubit_gate("H", 0)
    ground_state_2q.apply_single_qubit_gate("H", 1)
    ground_state_2q.apply_two_qubit_gate("CNOT", 0, 1)
    sv = ground_state_2q.statevector.data
    assert abs(np.linalg.norm(sv) - 1.0) < 1e-10


# ─── Gate catalogue completeness ──────────────────────────────────────────────

def test_all_single_gates_have_required_fields():
    required = {"name", "symbol", "params", "color", "desc"}
    for key, info in SINGLE_QUBIT_GATES.items():
        missing = required - set(info.keys())
        assert not missing, f"Gate {key} missing: {missing}"

def test_all_two_gates_have_required_fields():
    required = {"name", "symbol", "params", "color", "desc"}
    for key, info in TWO_QUBIT_GATES.items():
        missing = required - set(info.keys())
        assert not missing, f"Gate {key} missing: {missing}"

def test_no_three_qubit_gates():
    # Ensure no gate in catalogue requires 3+ qubits
    all_gates = {**SINGLE_QUBIT_GATES, **TWO_QUBIT_GATES}
    for key in all_gates:
        assert key not in {"CCX", "CSWAP", "CCZ"}, f"3-qubit gate {key} found in catalogue"
