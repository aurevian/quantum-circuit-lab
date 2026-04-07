# Gate Reference

Complete technical reference for all gates in Quantum Circuit Lab.

---

## Single-Qubit Gates

### Pauli Gates

| Gate | Symbol | Matrix | Effect on |0⟩ | Effect on |1⟩ |
|------|--------|--------|-----------|-----------| 
| Pauli-X | `X` | [[0,1],[1,0]] | → \|1⟩ | → \|0⟩ |
| Pauli-Y | `Y` | [[0,-i],[i,0]] | → i\|1⟩ | → -i\|0⟩ |
| Pauli-Z | `Z` | [[1,0],[0,-1]] | → \|0⟩ | → -\|1⟩ |
| Identity | `I` | [[1,0],[0,1]] | → \|0⟩ | → \|1⟩ |

### Hadamard Gate

```
H = (1/√2) * [[1, 1], [1,-1]]
```

Creates equal superposition: |0⟩ → (|0⟩ + |1⟩)/√2

### Phase Gates

| Gate | Symbol | Effect on |1⟩ |
|------|--------|-----------|
| S | `S` | → i\|1⟩ (π/2 phase) |
| T | `T` | → e^(iπ/4)\|1⟩ (π/4 phase) |
| S† | `Sdg` | → -i\|1⟩ (inverse S) |
| T† | `Tdg` | → e^(-iπ/4)\|1⟩ (inverse T) |

### Rotation Gates (Parametric)

These gates use the encoding formula:

```
θ = α_gate × x_i × π
```

where `α_gate` is the gate scale (remembered until reset) and `x_i` is the data input value.

**Rx(θ)** — Rotation around the X-axis:
```
Rx(θ) = [[cos(θ/2),  -i·sin(θ/2)],
          [-i·sin(θ/2), cos(θ/2)]]
```

**Ry(θ)** — Rotation around the Y-axis:
```
Ry(θ) = [[cos(θ/2), -sin(θ/2)],
          [sin(θ/2),  cos(θ/2)]]
```

**Rz(θ)** — Rotation around the Z-axis:
```
Rz(θ) = [[e^(-iθ/2),      0    ],
          [    0,       e^(iθ/2)]]
```

Special cases:
- Rx(π) = −iX (bit flip with global phase)
- Ry(π/2) = creates equal superposition from |0⟩
- Rz(π) = iZ (phase flip with global phase)

---

## Two-Qubit Gates

Convention: first listed qubit is **control**, second is **target**.

### CNOT (CX)

Flips the target qubit if and only if the control qubit is |1⟩.

```
CX = [[1,0,0,0],
      [0,1,0,0],
      [0,0,0,1],
      [0,0,1,0]]
```

Used with H to create Bell states:
```
H(q0) → CNOT(q0→q1) → (|00⟩ + |11⟩)/√2
```

### CZ

Applies a Z phase to the target if control is |1⟩. Symmetric in control/target.

```
CZ = [[1,0,0, 0],
      [0,1,0, 0],
      [0,0,1, 0],
      [0,0,0,-1]]
```

### CY, CH

Controlled-Y and Controlled-Hadamard — apply Y or H to the target conditionally.

### SWAP

Exchanges the quantum states of two qubits:
```
|ψ₀⟩|ψ₁⟩ → |ψ₁⟩|ψ₀⟩
```

### Controlled Rotations (Parametric)

CRx(θ), CRy(θ), CRz(θ) apply the corresponding rotation to the target qubit conditionally on the control being |1⟩. Same θ = α × x_i × π encoding applies.

---

## Gate Scale Encoding

The formula **θ = α × x_i × π** is the standard classical-to-quantum data encoding strategy used in variational quantum circuits (VQCs) and quantum machine learning (QML).

- **α** acts as a learnable weight — analogous to a neural network weight scaling a data input.
- **x_i ∈ ℝ** is a classical data value (feature) from a dataset.
- Multiplying by **π** maps the data to the natural period of quantum rotations.

This encoding appears in the literature as *angle encoding* or *dense angle encoding* and is used in architectures like the QSNN (Quantum Spiking Neural Network) and GIDE+QCPR pipelines.

**Example — Rz encoding:**

| α_rz | x_i | θ (rad) | θ (°) |
|-------|------|---------|-------|
| 1.0 | 0.0 | 0.000 | 0.0 |
| 1.0 | 0.5 | 1.571 | 90.0 |
| 1.0 | 1.0 | 3.142 | 180.0 |
| 0.5 | 0.5 | 0.785 | 45.0 |
| 2.0 | 0.25 | 1.571 | 90.0 |

---

## Bloch Sphere Representation

For a single qubit in state |ψ⟩ = α|0⟩ + β|1⟩, the Bloch vector is:

```
x = 2·Re(α*β)
y = 2·Im(α*β)  
z = |α|² − |β|²
```

For multi-qubit systems, the Bloch vector for qubit q is computed from its **reduced density matrix**, obtained by tracing out all other qubits:

```
ρ_q = Tr_{≠q}[|ψ⟩⟨ψ|]
```

This correctly handles entangled states — the reduced density matrix of an entangled qubit is a mixed state, and its Bloch vector lies strictly inside the sphere (|r| < 1).

---

## von Neumann Entropy

After each gate, the entropy is computed as:

```
S = −∑ᵢ pᵢ log₂(pᵢ)
```

where pᵢ are the measurement probabilities in the computational basis.

Entropy bounds:
- **S = 0** — pure computational basis state (e.g., |0…0⟩)
- **S = n** — maximally mixed state (uniform superposition over all 2ⁿ basis states)
- Entangling gates (CNOT, CZ, …) generally increase entropy
- Pauli gates (X, Y, Z) do not change entropy
- Rotation gates change entropy depending on the initial state and angle
