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

    # Palette scientifique cohérente (bleu nuit + bordeaux + vert cible)
    COLOR_PRIMARY   = "#1f4e8c"   # bleu nuit
    COLOR_SECONDARY = "#c0392b"   # bordeaux
    COLOR_TARGET    = "#27ae60"   # vert
    COLOR_ANNOTATE  = "#8e44ad"   # violet (points remarquables)
    COLOR_GRID      = "#cccccc"

    fig, ax = plt.subplots(figsize=(10, 6), dpi=dpi)
    fig.patch.set_facecolor("#fafafa")
    ax.set_facecolor("#ffffff")

    # Courbe principale (marqueurs + ligne)
    ax.plot(xs, ys, marker="o", markersize=4.5, linewidth=1.6,
            color=COLOR_PRIMARY, label=curve.kind.value,
            markeredgecolor="white", markeredgewidth=0.6, zorder=3)

    # Serie secondaire si présente
    if curve.secondary_points:
        sec_xs = [p.n for p in curve.secondary_points if p.y_float is not None]
        sec_ys = [p.y_float for p in curve.secondary_points if p.y_float is not None]
        ax.plot(sec_xs, sec_ys, marker="s", markersize=4.0, linewidth=1.3,
                color=COLOR_SECONDARY, linestyle="--",
                label=curve.secondary_label,
                markeredgecolor="white", markeredgewidth=0.5, zorder=3)

    # Ligne de reference
    if curve.target_line is not None:
        ax.axhline(curve.target_line, color=COLOR_TARGET, linestyle=":",
                   linewidth=1.8,
                   label=curve.target_label or f"cible {curve.target_line:.4g}",
                   zorder=2)

    # Annotations sur points remarquables (premier, dernier, extremums)
    if len(pts) >= 2 and curve.target_line is not None:
        # Premier point
        ax.annotate(
            f"{ys[0]:.4f}",
            xy=(xs[0], ys[0]),
            xytext=(8, 8), textcoords="offset points",
            fontsize=8, color=COLOR_ANNOTATE,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=COLOR_ANNOTATE, lw=0.7, alpha=0.85),
            zorder=4,
        )
        # Dernier point
        ax.annotate(
            f"{ys[-1]:.4f}",
            xy=(xs[-1], ys[-1]),
            xytext=(-50, 8), textcoords="offset points",
            fontsize=8, color=COLOR_ANNOTATE,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=COLOR_ANNOTATE, lw=0.7, alpha=0.85),
            zorder=4,
        )
        # Point divergent max (si distance a la cible > 5%)
        if curve.target_line is not None:
            distances = [abs(y - curve.target_line) for y in ys]
            i_max = distances.index(max(distances))
            if distances[i_max] > 0.05 and i_max not in (0, len(ys) - 1):
                ax.annotate(
                    f"max ecart\n{ys[i_max]:.4f}",
                    xy=(xs[i_max], ys[i_max]),
                    xytext=(10, -30), textcoords="offset points",
                    fontsize=7.5, color=COLOR_ANNOTATE,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white",
                              ec=COLOR_ANNOTATE, lw=0.7, alpha=0.85),
                    arrowprops=dict(arrowstyle="->", color=COLOR_ANNOTATE,
                                    lw=0.7, alpha=0.7),
                    zorder=4,
                )

    # Titre et axes
    ax.set_title(curve.title, fontsize=13, fontweight="bold", pad=15,
                 color="#222222")
    ax.set_xlabel(curve.x_label, fontsize=10.5, color="#444444")
    ax.set_ylabel(curve.y_label, fontsize=10.5, color="#444444")
    ax.grid(True, alpha=0.4, linestyle=":", color=COLOR_GRID, zorder=1)
    ax.legend(loc="best", fontsize=9.5, framealpha=0.92, edgecolor="#888888")

    # Spines plus douces
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#888888")
        ax.spines[spine].set_linewidth(0.8)

    # Footer scientifique (formule + timestamp)
    footer = f"Formule : {curve.formula}    |    Genere le : {curve.generated_at[:19]}Z"
    fig.text(0.5, 0.01, footer, ha="center", fontsize=7.5,
             style="italic", color="#555555")
    # Watermark Gabriel
    fig.text(0.99, 0.01, "Gabriel Multi-Loop Agent  -  Methode Spectrale Savard",
             ha="right", fontsize=6.5, color="#888888", style="italic")

    plt.tight_layout(rect=[0, 0.035, 1, 1])
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
