# Changelog

All notable changes to Quantum Circuit Lab are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2025

### Added
- **3-stage interactive workflow**: Setup → Build → Final Results
- **12 single-qubit gates**: H, X, Y, Z, S, T, S†, T†, Rx(θ), Ry(θ), Rz(θ), I
- **8 two-qubit gates**: CNOT, CZ, CY, SWAP, CH, CRx(θ), CRy(θ), CRz(θ)
- **Gate scale system**: parametric gates use θ = α × x_i × π; scale α remembered until circuit reset
- **Amplitude validation**: input magnitudes must lie in user-specified [min, max] range
- **Exact statevector simulation** via Qiskit `Statevector.evolve()`
- **Bloch sphere visualization** per qubit via partial trace of the density matrix
- **Probability histogram** after each gate application
- **Statevector amplitude table** with Re, Im, |ψ|, probability columns
- **von Neumann entropy timeline** across the full gate sequence
- **Annotated operation history** with gate description, entropy delta, and parametric details
- **Full final report**: circuit, statevector, probabilities, Bloch spheres, history
- **27 unit tests** covering engine correctness, edge cases, and gate catalogue integrity
- **GitHub Actions CI** across Python 3.10, 3.11, 3.12
