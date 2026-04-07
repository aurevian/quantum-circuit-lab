# Worked Examples

Step-by-step examples demonstrating common quantum circuit patterns in Quantum Circuit Lab.

---

## 1. Bell State (2 qubits)

The Bell state Φ⁺ = (|00⟩ + |11⟩)/√2 is the canonical maximally entangled 2-qubit state.

**Setup:**
- Qubits: 2
- Amplitude min: 0, max: 1
- Initial state: `1 0 0 0` (|00⟩)

**Gate sequence:**

| Step | Gate | Qubit | Effect |
|------|------|-------|--------|
| 1 | H | q0 | (|00⟩ + |10⟩)/√2 |
| 2 | CNOT | ctrl=q0, tgt=q1 | (|00⟩ + |11⟩)/√2 |

**Expected output:**
```
Probabilities:  |00⟩ = 0.5,  |11⟩ = 0.5
Entropy:        1.0 bit  (maximally entangled for 2 qubits)
Bloch vectors:  both at origin (|x|=|y|=|z|=0) — mixed reduced states
```

---

## 2. GHZ State (3 qubits)

The Greenberger–Horne–Zeilinger state: (|000⟩ + |111⟩)/√2.

**Setup:**
- Qubits: 3
- Initial state: `1 0 0 0 0 0 0 0` (|000⟩)

**Gate sequence:**

| Step | Gate | Qubit |
|------|------|-------|
| 1 | H | q0 |
| 2 | CNOT | ctrl=q0, tgt=q1 |
| 3 | CNOT | ctrl=q0, tgt=q2 |

**Expected output:**
```
Probabilities:  |000⟩ = 0.5,  |111⟩ = 0.5
Entropy:        1.0 bit
```

---

## 3. Quantum Fourier Transform (2 qubits)

A 2-qubit QFT on input |01⟩.

**Setup:**
- Qubits: 2
- Initial state: `0 1 0 0` (|01⟩)

**Gate sequence:**

| Step | Gate | Detail |
|------|------|--------|
| 1 | H | q0 |
| 2 | CRz(π/2) | ctrl=q1, tgt=q0; set α_crz=0.5, x_i=1.0 → θ=π/2 |
| 3 | H | q1 |
| 4 | SWAP | q0 ↔ q1 |

---

## 4. Data Encoding with Parametric Gates (QML)

Encoding a classical data point [0.3, 0.7] as rotation angles.

**Setup:**
- Qubits: 2
- Initial state: `1 0 0 0` (|00⟩)

**Gate sequence:**

| Step | Gate | α (scale) | x_i | θ = α × x_i × π |
|------|------|-----------|-----|-----------------|
| 1 | Ry | α_ry = 1.0 | 0.3 | 0.942 rad |
| 2 | Ry on q1 | α_ry = 1.0 | 0.7 | 2.199 rad |

This encodes the two features as independent rotation angles on separate qubits, the standard *angle encoding* used in QML.

---

## 5. Custom Initial State

Starting from a non-computational-basis state.

**Setup:**
- Qubits: 1
- Amplitude min: 0.0, max: 1.0
- Initial state: `0.6 0.8` (normalized to |ψ⟩ = 0.6|0⟩ + 0.8|1⟩)

**Check:**
```
|0.6|² + |0.8|² = 0.36 + 0.64 = 1.0  ✓  (already unit norm)
```

Apply H gate:
```
H|ψ⟩ = 0.6·H|0⟩ + 0.8·H|1⟩
      = 0.6·(|0⟩+|1⟩)/√2 + 0.8·(|0⟩-|1⟩)/√2
      = (1.4/√2)|0⟩ + (-0.2/√2)|1⟩

P(0) ≈ 0.98,  P(1) ≈ 0.02
```

---

## 6. Amplitude Range Validation

The app enforces that all input magnitudes lie in [min, max].

**Valid input (min=0, max=1):**
```
1 0 0 0          ✓  magnitudes: 1.0, 0.0, 0.0, 0.0 — all in [0, 1]
0.5+0.5j 0 0 0   ✓  |0.5+0.5j| = 0.707 — in [0, 1]
```

**Invalid input (min=0, max=1):**
```
2 0 0 0          ✗  magnitude 2.0 > max 1.0 — rejected with error
1 1 1 1 1 1 1 1  ✗  wrong length for 2-qubit (need 4) — rejected with error
```
