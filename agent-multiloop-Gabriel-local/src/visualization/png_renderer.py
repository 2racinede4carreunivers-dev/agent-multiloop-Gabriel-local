"""Renderer PNG (matplotlib) pour CurveData.

Genere une figure PNG haute resolution adaptee aux articles scientifiques.
Si matplotlib n'est pas disponible, leve une ImportError explicite.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .curves import CurveData

try:
    import matplotlib
    matplotlib.use("Agg")  # Backend non-interactif, pas de display requis
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def _slugify(s: str) -> str:
    """Convertit une string en nom de fichier safe."""
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    out = []
    for c in s:
        if c in keep:
            out.append(c)
        elif c.isspace() or c in "()":
            out.append("_")
    return "".join(out).strip("_") or "curve"


def render_png(
    curve: CurveData,
    output_dir: Path | str,
    dpi: int = 150,
    filename: Optional[str] = None,
) -> Path:
    """Rend une CurveData en PNG haute resolution.

    Args:
        curve: CurveData a rendre.
        output_dir: repertoire de sortie (cree si absent).
        dpi: resolution (150 = bonne qualite article, 300 = print).
        filename: nom du fichier (sans extension). Defaut : auto-genere.

    Returns:
        Path du PNG cree.

    Raises:
        ImportError: si matplotlib n'est pas installe.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "matplotlib n'est pas installe. Installez-le via 'pip install matplotlib' "
            "ou utilisez render_ascii / render_table comme alternative."
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        filename = f"{ts}_{_slugify(curve.kind.value)}_n{curve.n_min}-{curve.n_max}_{curve.scale}"
    out_path = output_dir / f"{filename}.png"

    pts = [p for p in curve.points if p.y_float is not None]
    if not pts:
        raise ValueError(f"Aucun point a tracer pour {curve.kind.value}")

    xs = [p.n for p in pts]
    ys = [p.y_float for p in pts]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=dpi)

    # Style scientifique sobre
    ax.plot(xs, ys, marker="o", markersize=3.5, linewidth=1.3,
            color="#1f4e8c", label=curve.kind.value)

    # Serie secondaire
    if curve.secondary_points:
        sec_xs = [p.n for p in curve.secondary_points if p.y_float is not None]
        sec_ys = [p.y_float for p in curve.secondary_points if p.y_float is not None]
        ax.plot(sec_xs, sec_ys, marker="s", markersize=3.0, linewidth=1.0,
                color="#c0392b", linestyle="--", label=curve.secondary_label)

    # Ligne de reference
    if curve.target_line is not None:
        ax.axhline(curve.target_line, color="#27ae60", linestyle=":",
                   linewidth=1.5,
                   label=curve.target_label or f"cible {curve.target_line:.4g}")

    ax.set_title(curve.title, fontsize=12, fontweight="bold")
    ax.set_xlabel(curve.x_label, fontsize=10)
    ax.set_ylabel(curve.y_label, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle=":")
    ax.legend(loc="best", fontsize=9, framealpha=0.9)

    # Footer scientifique
    footer = f"Formule : {curve.formula}    |    Genere le : {curve.generated_at[:19]}Z"
    fig.text(0.5, 0.01, footer, ha="center", fontsize=7, style="italic", color="#555555")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return out_path
