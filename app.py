"""
app.py
Qiskit Interactive Quantum Circuit Builder — Streamlit Application
"""

import streamlit as st
import numpy as np
import re
from quantum_engine import (
    QuantumCircuitSession,
    SINGLE_QUBIT_GATES,
    TWO_QUBIT_GATES,
    normalize_state,
)
from visualizer import (
    probability_histogram,
    statevector_plot,
    bloch_sphere,
    multi_bloch_panel,
    entropy_timeline,
)

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum Circuit Lab",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,700;1,400&family=Outfit:wght@300;400;500;600;700;800&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,300;1,400&display=swap');

  :root {
    --bg:       #08090f;
    --panel:    #0f1320;
    --panel2:   #131929;
    --border:   #1a2540;
    --cyan:     #00c2ff;
    --cyan2:    #00eaff;
    --accent:   #6d28d9;
    --accent2:  #8b5cf6;
    --green:    #86efac;
    --red:      #f87171;
    --orange:   #fb923c;
    --text:     #dde4f0;
    --sub:      #4d6080;
    --sub2:     #7a93b8;
  }

  html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif;
  }

  /* ── Sidebar ─────────────────────────────────────────────── */
  [data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid var(--border) !important;
  }
  [data-testid="stSidebar"] * { color: var(--text) !important; }

  /* ── Header ──────────────────────────────────────────────── */
  .qlab-header {
    background: linear-gradient(160deg, #0b1225 0%, #08090f 60%, #0b0d18 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 36px 22px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .qlab-header::before {
    content: '';
    position: absolute;
    top: -80px; right: -60px;
    width: 340px; height: 340px;
    background: radial-gradient(circle, rgba(0,194,255,0.07) 0%, transparent 65%);
    pointer-events: none;
  }
  .qlab-header::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 20%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(109,40,217,0.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .qlab-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 400;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--sub2);
    margin-bottom: 8px;
  }
  .qlab-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 0 0 4px 0;
  }
  .qlab-title span {
    background: linear-gradient(90deg, var(--cyan) 0%, var(--cyan2) 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .qlab-author-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 12px;
  }
  .qlab-rule {
    height: 1px;
    width: 28px;
    background: linear-gradient(90deg, transparent, var(--sub));
  }
  .qlab-author {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 400;
    font-style: italic;
    color: var(--sub2);
    letter-spacing: 0.06em;
  }
  .qlab-badges {
    display: flex;
    gap: 6px;
    margin-top: 14px;
    flex-wrap: wrap;
  }
  .qlab-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid;
  }
  .badge-q  { color: var(--cyan);   border-color: rgba(0,194,255,0.3);  background: rgba(0,194,255,0.05); }
  .badge-sv { color: var(--green);  border-color: rgba(134,239,172,0.3); background: rgba(134,239,172,0.05); }
  .badge-i  { color: var(--accent2);border-color: rgba(139,92,246,0.3); background: rgba(139,92,246,0.05); }

  /* ── Cards ───────────────────────────────────────────────── */
  .q-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
  }
  .q-card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 500;
    color: var(--sub2);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 14px;
  }

  /* ── Buttons ─────────────────────────────────────────────── */
  .stButton > button {
    background: var(--panel2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
  }
  .stButton > button:hover {
    background: rgba(0,194,255,0.07) !important;
    border-color: rgba(0,194,255,0.4) !important;
    color: var(--cyan) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,194,255,0.1);
  }

  /* ── Info boxes ──────────────────────────────────────────── */
  .q-info {
    background: rgba(0,194,255,0.05);
    border: 1px solid rgba(0,194,255,0.18);
    border-radius: 8px;
    padding: 11px 15px;
    font-size: 0.77rem;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.65;
    margin-bottom: 10px;
  }
  .q-warn {
    background: rgba(251,146,60,0.07);
    border: 1px solid rgba(251,146,60,0.28);
    border-radius: 8px;
    padding: 11px 15px;
    font-size: 0.77rem;
    color: var(--orange);
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.65;
    margin-bottom: 10px;
  }
  .q-error {
    background: rgba(248,113,113,0.07);
    border: 1px solid rgba(248,113,113,0.32);
    border-radius: 8px;
    padding: 11px 15px;
    font-size: 0.77rem;
    color: var(--red);
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.65;
    margin-bottom: 10px;
  }
  .q-formula {
    background: rgba(109,40,217,0.08);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--accent2);
    line-height: 1.75;
    margin-top: 8px;
  }
  .q-scale-ok {
    background: rgba(134,239,172,0.05);
    border: 1px solid rgba(134,239,172,0.22);
    border-radius: 8px;
    padding: 9px 13px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: var(--green);
    margin-bottom: 8px;
  }

  /* ── History records ─────────────────────────────────────── */
  .step-record {
    background: rgba(15,19,32,0.7);
    border-left: 3px solid var(--cyan);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
  }
  .step-record .gate-label { font-weight: 700; font-size: 0.86rem; }
  .step-record .step-desc  { color: var(--sub2); margin-top: 4px; font-size: 0.71rem; }

  /* ── Statevector table ───────────────────────────────────── */
  .sv-row {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
  }
  .sv-basis { color: var(--cyan);  min-width: 68px; }
  .sv-amp   { color: var(--text);  flex: 1; font-size: 0.7rem; }
  .sv-prob  { color: var(--green); min-width: 72px; text-align: right; }

  /* ── Circuit block ───────────────────────────────────────── */
  .circuit-block {
    background: #05070d;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    font-size: 0.7rem;
    line-height: 1.6;
    color: var(--green);
    font-family: 'JetBrains Mono', monospace;
  }

  /* ── Final banner ────────────────────────────────────────── */
  .final-card {
    background: linear-gradient(135deg, rgba(0,194,255,0.04), rgba(109,40,217,0.05));
    border: 1px solid rgba(0,194,255,0.25);
    border-radius: 12px;
    padding: 28px;
    text-align: center;
  }
  .final-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--cyan);
    margin-bottom: 6px;
  }

  /* ── Inputs ──────────────────────────────────────────────── */
  .stNumberInput input, .stTextInput input, .stTextArea textarea {
    background: #080c16 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
  }
  .stSelectbox > div > div {
    background: #080c16 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
  }
  .stSelectbox label, .stNumberInput label, .stTextInput label,
  .stTextArea label, .stSlider label, .stRadio label,
  [data-testid="stWidgetLabel"] p {
    color: var(--sub2) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.66rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  /* ── Tabs ────────────────────────────────────────────────── */
  [data-baseweb="tab-list"] { background: var(--panel) !important; border-radius: 8px; }
  [data-baseweb="tab"]      { color: var(--sub2) !important; font-family: 'JetBrains Mono' !important; font-size: 0.76rem !important; }
  [aria-selected="true"]    { color: var(--cyan) !important; border-bottom: 2px solid var(--cyan) !important; }

  /* ── Metrics ─────────────────────────────────────────────── */
  div[data-testid="metric-container"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
  }
  div[data-testid="metric-container"] label { color: var(--sub2) !important; font-family: 'JetBrains Mono' !important; font-size: 0.65rem !important; }
  div[data-testid="metric-container"] div   { color: var(--cyan) !important; font-family: 'Outfit' !important; font-weight: 600; }

  .stMarkdown p { color: var(--text) !important; }
  hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Parametric gate sets ─────────────────────────────────────────────────────
PARAMETRIC_SINGLE = {"RX", "RY", "RZ"}
PARAMETRIC_TWO    = {"CRX", "CRY", "CRZ"}
PARAMETRIC_ALL    = PARAMETRIC_SINGLE | PARAMETRIC_TWO

SCALE_NAMES = {
    "RX":  "α_rx",  "RY":  "α_ry",  "RZ":  "α_rz",
    "CRX": "α_crx", "CRY": "α_cry", "CRZ": "α_crz",
}


# ─── Session state init ───────────────────────────────────────────────────────
def init_session():
    defaults = {
        "stage":         "setup",
        "session":       None,
        "n_qubits":      2,
        "val_min":       0.0,
        "val_max":       1.0,
        "selected_gate": None,
        "entropies":     [],
        "entropy_steps": [],
        "gate_scales":   {},    # {gate_key: alpha} — persists until full reset
        "pending":       None,  # {"kind", "key", "qubits"}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─── Utility functions ────────────────────────────────────────────────────────
def parse_amplitudes(raw: str, dim: int) -> np.ndarray:
    tokens = [t for t in re.split(r"[\s,;]+", raw.strip()) if t]
    if len(tokens) != dim:
        raise ValueError(f"Expected {dim} amplitudes, got {len(tokens)}.")
    result = []
    for t in tokens:
        try:
            result.append(complex(t))
        except ValueError:
            raise ValueError(f"Cannot parse '{t}' as a number.")
    return np.array(result, dtype=complex)


def validate_amplitudes(amps: np.ndarray, val_min: float, val_max: float):
    mags = np.abs(amps)
    lo = np.where(mags < val_min - 1e-9)[0]
    hi = np.where(mags > val_max + 1e-9)[0]
    if len(lo):
        raise ValueError(
            f"Magnitude(s) at index [{', '.join(map(str, lo[:4]))}] "
            f"are below min = {val_min:.3f}. All |ψᵢ| must be in [{val_min:.3f}, {val_max:.3f}]."
        )
    if len(hi):
        raise ValueError(
            f"Magnitude(s) at index [{', '.join(map(str, hi[:4]))}] "
            f"exceed max = {val_max:.3f}. All |ψᵢ| must be in [{val_min:.3f}, {val_max:.3f}]."
        )


def build_sv(n_qubits, raw_amps, val_min, val_max):
    dim = 2 ** n_qubits
    amps = parse_amplitudes(raw_amps, dim)
    validate_amplitudes(amps, val_min, val_max)
    return normalize_state(amps)


def entropy_of(probs: np.ndarray) -> float:
    p = probs[probs > 1e-12]
    return float(-np.sum(p * np.log2(p)))


def fmt_c(c: complex) -> str:
    r, i = float(np.real(c)), float(np.imag(c))
    return f"{r:+.4f}" if abs(i) < 1e-6 else f"{r:+.4f}{i:+.4f}j"


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qlab-header">
  <div class="qlab-eyebrow">⚛ &nbsp; Interactive Statevector Simulation</div>
  <div class="qlab-title">Quantum <span>Circuit Lab</span></div>
  <div class="qlab-author-wrap">
    <div class="qlab-rule"></div>
    <div class="qlab-author">Eren Bozkurt</div>
    <div class="qlab-rule"></div>
  </div>
  <div class="qlab-badges">
    <span class="qlab-badge badge-q">Qiskit 2.x</span>
    <span class="qlab-badge badge-sv">Exact Statevector</span>
    <span class="qlab-badge badge-i">Interactive</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# STAGE 1 — SETUP
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "setup":
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="q-card">', unsafe_allow_html=True)
        st.markdown('<div class="q-card-title">⚙ Circuit Configuration</div>', unsafe_allow_html=True)

        n_qubits = st.number_input("Number of Qubits", min_value=1, max_value=6, value=2, step=1)
        dim = 2 ** n_qubits
        st.markdown(
            f'<div class="q-info">State space: <b>{dim}</b> basis states — |{"0"*n_qubits}⟩ … |{"1"*n_qubits}⟩</div>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            val_min = st.number_input("Amplitude Min", value=0.0, step=0.1, format="%.3f")
        with c2:
            val_max = st.number_input("Amplitude Max", value=1.0, step=0.1, format="%.3f")

        range_ok = val_min < val_max
        if not range_ok:
            st.markdown('<div class="q-error">⚠ Min must be strictly less than Max.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="q-info">All |ψᵢ| must lie in <b>[{val_min:.3f}, {val_max:.3f}]</b>. '
                f'Inputs outside this range will be rejected.</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown('<div class="q-card-title">📡 Initial State Amplitudes</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="q-info">Enter <b>{dim}</b> values (real or complex).<br>'
            f'Example: <code>1 0 0 0</code> &nbsp;or&nbsp; <code>0.5+0.5j, 0.5-0.5j, 0, 0</code><br>'
            f'State is automatically normalized after validation.</div>',
            unsafe_allow_html=True
        )

        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            if st.button("|0…0⟩"):
                st.session_state["_preset"] = " ".join(["1"] + ["0"] * (dim - 1))
        with pc2:
            if st.button("Equal super."):
                st.session_state["_preset"] = " ".join(["1"] * dim)
        with pc3:
            if st.button("|1…1⟩"):
                st.session_state["_preset"] = " ".join(["0"] * (dim - 1) + ["1"])

        raw = st.text_area(
            f"Amplitudes ({dim} values)",
            value=st.session_state.get("_preset", " ".join(["1"] + ["0"] * (dim - 1))),
            height=80,
        )

        err, preview = None, None
        if range_ok:
            try:
                preview = build_sv(n_qubits, raw, val_min, val_max)
            except Exception as e:
                err = str(e)

        if err:
            st.markdown(f'<div class="q-error">⚠ {err}</div>', unsafe_allow_html=True)
        elif preview is not None:
            labels = [f"|{format(i, f'0{n_qubits}b')}⟩" for i in range(dim)]
            rows = "".join(
                f'<div class="sv-row"><span class="sv-basis">{lbl}</span>'
                f'<span class="sv-amp">{fmt_c(a)}</span>'
                f'<span class="sv-prob">p={abs(a)**2:.4f}</span></div>'
                for lbl, a in zip(labels, preview)
            )
            st.markdown("**Preview — Normalized Initial State:**")
            st.markdown(rows, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚀  Initialize Circuit", use_container_width=True,
                      disabled=(err is not None or preview is None or not range_ok)):
            sess = QuantumCircuitSession(n_qubits, preview)
            st.session_state.session       = sess
            st.session_state.n_qubits      = n_qubits
            st.session_state.val_min       = val_min
            st.session_state.val_max       = val_max
            st.session_state.stage         = "build"
            st.session_state.entropies     = [entropy_of(sess.probabilities)]
            st.session_state.entropy_steps = [0]
            # gate_scales preserved intentionally
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# STAGE 2 — BUILD
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "build":
    sess: QuantumCircuitSession = st.session_state.session
    n      = sess.n_qubits
    labels = sess.get_basis_labels()

    # ── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="q-card-title">🔬 Gate Palette</div>', unsafe_allow_html=True)

        gate_type = st.radio("Type", ["Single Qubit", "Two Qubit"],
                              horizontal=True, label_visibility="collapsed")
        st.markdown("---")

        # ── Gate selection ─────────────────────────────────────────────────
        if gate_type == "Single Qubit":
            qubit = st.selectbox("Target qubit", list(range(n)),
                                  format_func=lambda q: f"q{q}")
            cols = st.columns(3)
            for i, (key, info) in enumerate(SINGLE_QUBIT_GATES.items()):
                with cols[i % 3]:
                    if st.button(info["symbol"], key=f"sg_{key}", help=info["desc"]):
                        st.session_state.pending = {"kind": "single", "key": key,
                                                     "qubits": [qubit]}
        else:
            control = st.selectbox("Control", list(range(n)),
                                    format_func=lambda q: f"q{q}", key="ctrl_q")
            target_opts = [q for q in range(n) if q != control]
            if not target_opts:
                st.markdown('<div class="q-warn">Need ≥2 qubits.</div>', unsafe_allow_html=True)
            else:
                target = st.selectbox("Target", target_opts,
                                       format_func=lambda q: f"q{q}", key="tgt_q")
                cols = st.columns(2)
                for i, (key, info) in enumerate(TWO_QUBIT_GATES.items()):
                    with cols[i % 2]:
                        if st.button(info["symbol"], key=f"tg_{key}", help=info["desc"]):
                            st.session_state.pending = {"kind": "two", "key": key,
                                                         "qubits": [control, target]}

        # ── Parametric controls ────────────────────────────────────────────
        st.markdown("---")
        pending   = st.session_state.pending
        theta_val = None    # final angle
        xi_val    = None    # user data value
        scale_val = None    # confirmed alpha
        blocked   = False   # True when scale not yet confirmed

        if pending is not None:
            gate_key  = pending["key"]
            gdict     = SINGLE_QUBIT_GATES if pending["kind"] == "single" else TWO_QUBIT_GATES
            gate_info = gdict[gate_key]
            q_str = (f"q{pending['qubits'][0]}" if pending["kind"] == "single"
                     else f"ctrl=q{pending['qubits'][0]} → tgt=q{pending['qubits'][1]}")

            st.markdown(
                f'<div style="font-family:JetBrains Mono;font-size:0.7rem;margin-bottom:6px;">'
                f'<span style="color:var(--sub2);">Selected: </span>'
                f'<span style="color:var(--cyan);font-weight:700;">{gate_info["symbol"]}</span>'
                f'<span style="color:var(--sub2);"> on {q_str}</span></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="font-family:JetBrains Mono;font-size:0.68rem;'
                f'color:var(--sub);margin-bottom:10px;">{gate_info["desc"]}</div>',
                unsafe_allow_html=True
            )

            if gate_key in PARAMETRIC_ALL:
                sname  = SCALE_NAMES[gate_key]
                stored = st.session_state.gate_scales.get(gate_key)

                # ── Gate scale (first time only) ───────────────────────────
                if stored is None:
                    st.markdown(
                        f'<div class="q-warn">🔑 First use of <b>{gate_info["symbol"]}</b>.<br>'
                        f'Set gate scale <b>{sname}</b> — stored until full reset.</div>',
                        unsafe_allow_html=True
                    )
                    new_alpha = st.number_input(
                        f"Gate scale  {sname}",
                        value=1.0, step=0.05, format="%.4f",
                        key=f"alpha_input_{gate_key}",
                    )
                    if st.button(f"✅  Save {sname}", key=f"save_{gate_key}"):
                        st.session_state.gate_scales[gate_key] = float(new_alpha)
                        st.rerun()
                    blocked = True

                else:
                    st.markdown(
                        f'<div class="q-scale-ok">✓ {sname} = <b>{stored:.4f}</b> (remembered)</div>',
                        unsafe_allow_html=True
                    )
                    if st.button(f"✏  Change {sname}", key=f"chg_{gate_key}"):
                        del st.session_state.gate_scales[gate_key]
                        st.rerun()
                    scale_val = stored

                    # ── x_i input ──────────────────────────────────────────
                    xi_val = st.number_input(
                        "Data value  x_i",
                        value=0.5, step=0.05, format="%.4f",
                        key=f"xi_{gate_key}_{len(sess.history)}",
                        help="Value from dataset. Formula: θ = α × x_i × π",
                    )
                    theta_val = scale_val * xi_val * np.pi

                    st.markdown(
                        f'<div class="q-formula">'
                        f'θ &nbsp;=&nbsp; {sname} &nbsp;×&nbsp; x_i &nbsp;×&nbsp; π<br>'
                        f'&nbsp;&nbsp;=&nbsp; {scale_val:.4f} &nbsp;×&nbsp; {xi_val:.4f} &nbsp;×&nbsp; π<br>'
                        f'&nbsp;&nbsp;=&nbsp; <b>{theta_val:.5f}</b> rad'
                        f'&nbsp; ({np.degrees(theta_val):.2f}°)</div>',
                        unsafe_allow_html=True
                    )

        # ── Apply button ───────────────────────────────────────────────────
        st.markdown("---")

        if pending is not None and blocked:
            st.markdown(
                '<div class="q-warn">⚠ Confirm the gate scale above before applying.</div>',
                unsafe_allow_html=True
            )

        apply_ok = (
            pending is not None
            and not blocked
            and (pending["key"] not in PARAMETRIC_ALL or theta_val is not None)
        )

        if st.button("⚡  Apply Gate", disabled=not apply_ok,
                      use_container_width=True, type="primary"):
            try:
                if pending["kind"] == "single":
                    record = sess.apply_single_qubit_gate(
                        pending["key"], pending["qubits"][0], theta_val
                    )
                else:
                    record = sess.apply_two_qubit_gate(
                        pending["key"], pending["qubits"][0], pending["qubits"][1], theta_val
                    )
                # Attach xi/alpha metadata to record
                if pending["key"] in PARAMETRIC_ALL and xi_val is not None:
                    record["xi"]    = float(xi_val)
                    record["alpha"] = float(scale_val)
                st.session_state.pending = None
                st.session_state.entropies.append(entropy_of(sess.probabilities))
                st.session_state.entropy_steps.append(len(sess.history))
                st.rerun()
            except Exception as ex:
                st.error(str(ex))

        if st.button("❌  Cancel", use_container_width=True, disabled=(pending is None)):
            st.session_state.pending = None
            st.rerun()

        st.markdown("---")
        if st.button("🏁  Finalize Circuit", use_container_width=True):
            st.session_state.stage   = "done"
            st.session_state.pending = None
            st.rerun()
        if st.button("🔄  Full Reset", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── Metrics ────────────────────────────────────────────────────────────
    probs = sess.probabilities
    sv    = sess.statevector.data
    ent   = entropy_of(probs)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Qubits", n)
    with m2: st.metric("Gates Applied", sess.num_gates)
    with m3: st.metric("Entropy", f"{ent:.4f} bits")
    with m4: st.metric("Most Probable", labels[np.argmax(probs)])

    # ── Remembered scales panel ────────────────────────────────────────────
    if st.session_state.gate_scales:
        entries = " &nbsp;|&nbsp; ".join(
            f'<span style="color:var(--cyan);">{SCALE_NAMES[k]}</span>'
            f'<span style="color:var(--sub2);"> = </span>'
            f'<span style="color:var(--green);">{v:.4f}</span>'
            for k, v in st.session_state.gate_scales.items()
        )
        st.markdown(
            f'<div class="q-scale-ok" style="font-size:0.78rem;margin-top:8px;">'
            f'🔑 &nbsp;Remembered scales:&nbsp; {entries}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab_c, tab_sv, tab_bl, tab_h, tab_e = st.tabs([
        "🔌 Circuit", "📊 Statevector", "🌐 Bloch", "📜 History", "📈 Entropy"
    ])

    with tab_c:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown('<div class="q-card-title">📐 Circuit Diagram</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="circuit-block"><pre>{sess.get_circuit_ascii()}</pre></div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="q-card-title">📊 Probabilities</div>', unsafe_allow_html=True)
            st.plotly_chart(probability_histogram(labels, probs),
                            use_container_width=True, config={"displayModeBar": False})

    with tab_sv:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="q-card-title">🧮 Amplitude Table</div>', unsafe_allow_html=True)
            rows = "".join(
                f'<div class="sv-row"><span class="sv-basis">{lbl}</span>'
                f'<span class="sv-amp">{fmt_c(a)}</span>'
                f'<span class="sv-prob">p={abs(a)**2:.5f}</span></div>'
                for lbl, a in zip(labels, sv)
            )
            st.markdown(rows, unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="q-card-title">📉 Amplitude Chart</div>', unsafe_allow_html=True)
            st.plotly_chart(statevector_plot(labels, sv),
                            use_container_width=True, config={"displayModeBar": False})

    with tab_bl:
        st.markdown('<div class="q-card-title">🌐 Bloch Sphere</div>', unsafe_allow_html=True)
        bvecs = [sess.bloch_data_for_qubit(q) for q in range(n)]
        if n == 1:
            bx, by, bz = bvecs[0]
            st.plotly_chart(bloch_sphere(bx, by, bz, 0),
                            use_container_width=True, config={"displayModeBar": False})
        else:
            bq = st.selectbox("Focus qubit", list(range(n)),
                               format_func=lambda q: f"q{q}", key="bq")
            bx, by, bz = bvecs[bq]
            bc1, bc2 = st.columns([1, 2])
            with bc1:
                st.plotly_chart(bloch_sphere(bx, by, bz, bq),
                                use_container_width=True, config={"displayModeBar": False})
            with bc2:
                st.plotly_chart(multi_bloch_panel(bvecs),
                                use_container_width=True, config={"displayModeBar": False})

    with tab_h:
        st.markdown('<div class="q-card-title">📜 Operation History</div>', unsafe_allow_html=True)
        if not sess.history:
            st.markdown('<div class="q-info">No gates applied yet.</div>', unsafe_allow_html=True)
        else:
            for rec in reversed(sess.history):
                q_str = (f"q{rec['qubits'][0]}" if rec["kind"] == "single"
                         else f"ctrl=q{rec['qubits'][0]} → tgt=q{rec['qubits'][1]}")
                extra = ""
                if rec.get("xi") is not None:
                    sname = SCALE_NAMES.get(rec["gate_key"], "α")
                    extra = (f" &nbsp;·&nbsp; {sname}={rec['alpha']:.4f}"
                             f" &nbsp;·&nbsp; x_i={rec['xi']:.4f}"
                             f" &nbsp;·&nbsp; θ={rec['param']:.4f} rad")
                d = rec["delta_entropy"]
                arrow = "↑" if d > 0.005 else ("↓" if d < -0.005 else "→")
                st.markdown(
                    f'<div class="step-record">'
                    f'<span class="gate-label" style="color:{rec["color"]}">Step {rec["step"]} — {rec["gate_label"]}</span>'
                    f'<span style="color:var(--sub2);font-size:0.7rem;"> on {q_str}{extra} &nbsp; entropy {arrow} ({d:+.3f})</span>'
                    f'<div class="step-desc">💬 {rec["description"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    with tab_e:
        st.markdown('<div class="q-card-title">📈 von Neumann Entropy</div>', unsafe_allow_html=True)
        st.plotly_chart(entropy_timeline(st.session_state.entropy_steps, st.session_state.entropies),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div class="q-info">Current: <b>{ent:.5f} bits</b> &nbsp;·&nbsp; '
            f'max = {np.log2(2**n):.2f} bits (uniform superposition)</div>',
            unsafe_allow_html=True
        )

    # ── Latest gate effect ─────────────────────────────────────────────────
    if sess.history:
        latest = sess.history[-1]
        st.markdown("---")
        st.markdown('<div class="q-card-title">⚡ Latest Gate Effect</div>', unsafe_allow_html=True)
        lc1, lc2 = st.columns([2, 3])
        with lc1:
            formula_html = ""
            if latest.get("xi") is not None:
                sn = SCALE_NAMES.get(latest["gate_key"], "α")
                formula_html = (
                    f'<div class="q-formula" style="margin-top:12px;">'
                    f'θ = {sn} × x_i × π<br>'
                    f'&nbsp; = {latest["alpha"]:.4f} × {latest["xi"]:.4f} × π<br>'
                    f'&nbsp; = <b>{latest["param"]:.5f}</b> rad</div>'
                )
            st.markdown(
                f'<div class="q-card">'
                f'<span style="font-family:Outfit;font-size:1.5rem;color:{latest["color"]};font-weight:800;">'
                f'{latest["gate_label"]}</span><br>'
                f'<span style="color:var(--sub2);font-size:0.7rem;font-family:JetBrains Mono;">'
                f'{latest["gate_name"]}</span><br><br>'
                f'<span style="font-size:0.78rem;">{latest["description"]}</span>'
                f'{formula_html}</div>',
                unsafe_allow_html=True
            )
        with lc2:
            st.plotly_chart(
                probability_histogram(labels, latest["probabilities"],
                                      title=f"After {latest['gate_label']}"),
                use_container_width=True, config={"displayModeBar": False}
            )


# ════════════════════════════════════════════════════════════════════════════════
# STAGE 3 — FINAL RESULTS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "done":
    sess: QuantumCircuitSession = st.session_state.session
    n      = sess.n_qubits
    labels = sess.get_basis_labels()
    sv     = sess.statevector.data
    probs  = sess.probabilities
    ent    = entropy_of(probs)

    with st.sidebar:
        if st.button("◀  Back to Builder"):
            st.session_state.stage = "build"
            st.rerun()
        if st.button("🔄  New Circuit"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.markdown(
        f'<div class="final-card">'
        f'<div class="final-title">⚛ Circuit Complete</div>'
        f'<div style="color:var(--sub2);font-size:0.8rem;font-family:JetBrains Mono;">'
        f'{n} qubits &nbsp;·&nbsp; {sess.num_gates} gates &nbsp;·&nbsp; '
        f'entropy = {ent:.4f} bits &nbsp;·&nbsp; '
        f'dominant = {labels[np.argmax(probs)]} ({probs.max()*100:.1f}%)'
        f'</div></div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Qubits", n)
    with m2: st.metric("Total Gates", sess.num_gates)
    with m3: st.metric("Entropy", f"{ent:.4f} bits")
    with m4: st.metric("Circuit Depth", sess.circuit.depth())
    st.markdown("---")

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="q-card-title">📐 Final Circuit</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="circuit-block"><pre>{sess.get_circuit_ascii()}</pre></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="q-card-title">📊 Final Probabilities</div>', unsafe_allow_html=True)
        st.plotly_chart(probability_histogram(labels, probs, "Final Measurement"),
                        use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown('<div class="q-card-title">🧮 Final Statevector</div>', unsafe_allow_html=True)
        rows = "".join(
            f'<div class="sv-row"><span class="sv-basis">{lbl}</span>'
            f'<span class="sv-amp">{fmt_c(a)}</span>'
            f'<span class="sv-prob">p={abs(a)**2:.5f}</span></div>'
            for lbl, a in zip(labels, sv)
        )
        st.markdown(rows, unsafe_allow_html=True)
    with sc2:
        st.plotly_chart(statevector_plot(labels, sv),
                        use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")
    st.markdown('<div class="q-card-title">🌐 Final Bloch Spheres</div>', unsafe_allow_html=True)
    bvecs = [sess.bloch_data_for_qubit(q) for q in range(n)]
    if n == 1:
        bx, by, bz = bvecs[0]
        st.plotly_chart(bloch_sphere(bx, by, bz, 0),
                        use_container_width=True, config={"displayModeBar": False})
    else:
        st.plotly_chart(multi_bloch_panel(bvecs),
                        use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")
    st.markdown('<div class="q-card-title">📜 Annotated Gate History</div>', unsafe_allow_html=True)
    for rec in sess.history:
        q_str = (f"q{rec['qubits'][0]}" if rec["kind"] == "single"
                 else f"ctrl=q{rec['qubits'][0]} → tgt=q{rec['qubits'][1]}")
        extra = ""
        if rec.get("xi") is not None:
            sn = SCALE_NAMES.get(rec["gate_key"], "α")
            extra = (f" &nbsp;·&nbsp; {sn}={rec['alpha']:.4f}"
                     f" &nbsp;·&nbsp; x_i={rec['xi']:.4f}"
                     f" &nbsp;·&nbsp; θ={rec['param']:.5f} rad")
        d = rec["delta_entropy"]
        arrow = (f"↑ +{d:.3f}" if d > 0.001 else f"↓ {d:.3f}" if d < -0.001 else "→ ~0")
        top = labels[np.argmax(rec["probabilities"])]
        p   = float(np.max(rec["probabilities"]))
        st.markdown(
            f'<div class="step-record">'
            f'<span class="gate-label" style="color:{rec["color"]}">Step {rec["step"]} — {rec["gate_label"]}</span>'
            f'<span style="color:var(--sub2);font-size:0.7rem;"> on {q_str}{extra}'
            f' &nbsp;·&nbsp; entropy {arrow} bits &nbsp;·&nbsp; dominant: {top} ({p*100:.1f}%)</span>'
            f'<div class="step-desc">💬 {rec["description"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown('<div class="q-card-title">📈 Entropy Evolution</div>', unsafe_allow_html=True)
    st.plotly_chart(entropy_timeline(st.session_state.entropy_steps, st.session_state.entropies),
                    use_container_width=True, config={"displayModeBar": False})
