"""
visualizer.py
Plotly-based visualizations: probability histogram, Bloch sphere, statevector table.
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Optional, Tuple


# ─── Theme ────────────────────────────────────────────────────────────────────
BG       = "#0a0e1a"
PANEL    = "#111827"
BORDER   = "#1e2d40"
CYAN     = "#00d4ff"
ACCENT   = "#7c3aed"
TEXT     = "#e2e8f0"
SUBTEXT  = "#64748b"
GRID     = "#1e293b"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'JetBrains Mono', monospace", color=TEXT, size=12),
    margin=dict(l=40, r=20, t=40, b=40),
)


# ─── Probability Histogram ────────────────────────────────────────────────────

def probability_histogram(labels: List[str], probs: np.ndarray,
                           title: str = "Measurement Probabilities") -> go.Figure:
    colors = [CYAN if p > 0.01 else SUBTEXT for p in probs]
    bar_border = [ACCENT if p > 0.01 else GRID for p in probs]

    fig = go.Figure(go.Bar(
        x=labels,
        y=probs,
        marker=dict(
            color=colors,
            line=dict(color=bar_border, width=1.5),
            opacity=0.85,
        ),
        text=[f"{p:.3f}" if p > 0.005 else "" for p in probs],
        textposition="outside",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="<b>%{x}</b><br>P = %{y:.5f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(color=CYAN, size=14)),
        xaxis=dict(tickfont=dict(family="'JetBrains Mono'", size=10), gridcolor=GRID,
                   showline=True, linecolor=BORDER),
        yaxis=dict(range=[0, max(probs.max() * 1.25, 0.05)], gridcolor=GRID,
                   showline=True, linecolor=BORDER),
        **PLOTLY_LAYOUT,
    )
    return fig


# ─── Statevector Amplitude Plot ───────────────────────────────────────────────

def statevector_plot(labels: List[str], sv: np.ndarray) -> go.Figure:
    reals = np.real(sv)
    imags = np.imag(sv)
    mags  = np.abs(sv)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Re(ψ)",
        x=labels, y=reals,
        marker_color=CYAN, opacity=0.7,
        hovertemplate="<b>%{x}</b><br>Re = %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Im(ψ)",
        x=labels, y=imags,
        marker_color="#ff6b6b", opacity=0.7,
        hovertemplate="<b>%{x}</b><br>Im = %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        name="|ψ|",
        x=labels, y=mags,
        mode="markers+lines",
        marker=dict(color="#a9e34b", size=8, symbol="diamond"),
        line=dict(color="#a9e34b", width=1, dash="dot"),
        hovertemplate="<b>%{x}</b><br>|ψ| = %{y:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Statevector Amplitudes", font=dict(color=CYAN, size=14)),
        barmode="group",
        xaxis=dict(gridcolor=GRID, showline=True, linecolor=BORDER),
        yaxis=dict(gridcolor=GRID, showline=True, linecolor=BORDER, range=[-1.1, 1.1]),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor=BORDER, borderwidth=1),
        **PLOTLY_LAYOUT,
    )
    return fig


# ─── Bloch Sphere ─────────────────────────────────────────────────────────────

def bloch_sphere(x: float, y: float, z: float,
                 qubit_idx: int = 0) -> go.Figure:
    """Render a single-qubit Bloch sphere for qubit `qubit_idx`."""
    # Sphere surface
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    sx = np.outer(np.cos(u), np.sin(v))
    sy = np.outer(np.sin(u), np.sin(v))
    sz = np.outer(np.ones_like(u), np.cos(v))

    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=sx, y=sy, z=sz,
        opacity=0.08,
        colorscale=[[0, PANEL], [1, BORDER]],
        showscale=False,
        hoverinfo="skip",
    ))

    # Axes
    for axis, label, color in [
        ([[-1.3, 1.3], [0, 0], [0, 0]], "+X/-X", SUBTEXT),
        ([[0, 0], [-1.3, 1.3], [0, 0]], "+Y/-Y", SUBTEXT),
        ([[0, 0], [0, 0], [-1.3, 1.3]], "|1⟩/|0⟩", SUBTEXT),
    ]:
        fig.add_trace(go.Scatter3d(
            x=axis[0], y=axis[1], z=axis[2],
            mode="lines",
            line=dict(color=GRID, width=2),
            hoverinfo="skip", showlegend=False,
        ))

    # Axis labels
    for pos, lbl in [
        ([0, 0, 1.45], "|0⟩"), ([0, 0, -1.45], "|1⟩"),
        ([1.45, 0, 0], "+X"), ([-1.45, 0, 0], "-X"),
        ([0, 1.45, 0], "+Y"), ([0, -1.45, 0], "-Y"),
    ]:
        fig.add_trace(go.Scatter3d(
            x=[pos[0]], y=[pos[1]], z=[pos[2]],
            mode="text", text=[lbl],
            textfont=dict(color=SUBTEXT, size=10),
            hoverinfo="skip", showlegend=False,
        ))

    # State vector arrow
    fig.add_trace(go.Scatter3d(
        x=[0, x], y=[0, y], z=[0, z],
        mode="lines+markers",
        line=dict(color=CYAN, width=6),
        marker=dict(size=[0, 10], color=CYAN, symbol=["circle", "circle"]),
        name=f"q{qubit_idx} state",
        hovertemplate=f"<b>q{qubit_idx}</b><br>x={x:.3f} y={y:.3f} z={z:.3f}<extra></extra>",
    ))

    # Projection lines (dashed)
    fig.add_trace(go.Scatter3d(
        x=[x, x, 0], y=[y, 0, 0], z=[0, 0, 0],
        mode="lines",
        line=dict(color=ACCENT, width=2, dash="dash"),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter3d(
        x=[x, x], y=[y, y], z=[0, z],
        mode="lines",
        line=dict(color=ACCENT, width=2, dash="dash"),
        hoverinfo="skip", showlegend=False,
    ))

    fig.update_layout(
        title=dict(text=f"Bloch Sphere — q{qubit_idx}", font=dict(color=CYAN, size=14)),
        scene=dict(
            xaxis=dict(showbackground=False, gridcolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=SUBTEXT, size=8)),
            yaxis=dict(showbackground=False, gridcolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=SUBTEXT, size=8)),
            zaxis=dict(showbackground=False, gridcolor=GRID, zerolinecolor=GRID,
                       tickfont=dict(color=SUBTEXT, size=8)),
            bgcolor="rgba(0,0,0,0)",
            aspectmode="cube",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'JetBrains Mono', monospace", color=TEXT),
        margin=dict(l=0, r=0, t=40, b=0),
        height=380,
        legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor=BORDER, x=0.02, y=0.98),
    )
    return fig


# ─── Multi-Qubit Bloch Panel ──────────────────────────────────────────────────

def multi_bloch_panel(bloch_vectors: List[Tuple[float, float, float]]) -> go.Figure:
    """Mini Bloch spheres for all qubits in a single figure."""
    n = len(bloch_vectors)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols

    specs = [[{"type": "scatter3d"} for _ in range(cols)] for _ in range(rows)]
    titles = [f"q{i}" for i in range(n)]
    fig = make_subplots(rows=rows, cols=cols, specs=specs, subplot_titles=titles)

    for idx, (bx, by, bz) in enumerate(bloch_vectors):
        row = idx // cols + 1
        col = idx % cols + 1

        # Sphere outline (latitude circles)
        for phi in [np.pi / 4, np.pi / 2, 3 * np.pi / 4]:
            t = np.linspace(0, 2 * np.pi, 40)
            cx = np.cos(t) * np.sin(phi)
            cy = np.sin(t) * np.sin(phi)
            cz = np.full_like(t, np.cos(phi))
            fig.add_trace(go.Scatter3d(
                x=cx, y=cy, z=cz, mode="lines",
                line=dict(color=GRID, width=1), hoverinfo="skip", showlegend=False,
            ), row=row, col=col)

        # Axes
        for xs, ys, zs in [
            ([-1.2, 1.2], [0, 0], [0, 0]),
            ([0, 0], [-1.2, 1.2], [0, 0]),
            ([0, 0], [0, 0], [-1.2, 1.2]),
        ]:
            fig.add_trace(go.Scatter3d(
                x=xs, y=ys, z=zs, mode="lines",
                line=dict(color=BORDER, width=1), hoverinfo="skip", showlegend=False,
            ), row=row, col=col)

        # State vector
        color = CYAN if abs(bz) < 0.99 else ("#a9e34b" if bz > 0 else "#ff6b6b")
        fig.add_trace(go.Scatter3d(
            x=[0, bx], y=[0, by], z=[0, bz], mode="lines+markers",
            line=dict(color=color, width=5),
            marker=dict(size=[0, 8], color=color),
            name=f"q{idx}", showlegend=False,
            hovertemplate=f"q{idx}: ({bx:.2f},{by:.2f},{bz:.2f})<extra></extra>",
        ), row=row, col=col)

    fig.update_layout(
        title=dict(text="Bloch Vectors — All Qubits", font=dict(color=CYAN, size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'JetBrains Mono'", color=TEXT),
        margin=dict(l=0, r=0, t=60, b=0),
        height=280 * rows,
    )
    # Make all 3d scenes transparent
    for i in range(1, n + 1):
        key = "scene" if i == 1 else f"scene{i}"
        fig.update_layout(**{
            key: dict(
                xaxis=dict(showbackground=False, gridcolor=GRID),
                yaxis=dict(showbackground=False, gridcolor=GRID),
                zaxis=dict(showbackground=False, gridcolor=GRID),
                bgcolor="rgba(0,0,0,0)",
                aspectmode="cube",
            )
        })
    return fig


# ─── Entropy Timeline ─────────────────────────────────────────────────────────

def entropy_timeline(steps: List[int], entropies: List[float]) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=steps, y=entropies,
        mode="lines+markers",
        line=dict(color=CYAN, width=2.5),
        marker=dict(color=ACCENT, size=8, symbol="circle"),
        fill="tozeroy",
        fillcolor=f"rgba(0,212,255,0.07)",
        hovertemplate="<b>Step %{x}</b><br>Entropy = %{y:.4f} bits<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="von Neumann Entropy Timeline", font=dict(color=CYAN, size=14)),
        xaxis=dict(title="Step", gridcolor=GRID, dtick=1),
        yaxis=dict(title="Entropy (bits)", gridcolor=GRID),
        **PLOTLY_LAYOUT,
    )
    return fig
