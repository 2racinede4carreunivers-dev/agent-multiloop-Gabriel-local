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
    primary_label = curve.primary_label or curve.kind.value
    ax.plot(xs, ys, marker="o", markersize=4.5, linewidth=1.6,
            color=COLOR_PRIMARY, label=primary_label,
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

    # v3.25 : Resume critique + legende des axes sous le graphique
    # Reserve une zone en bas de la figure pour ces annotations
    has_summary = bool(curve.critical_summary)
    has_axis_legend = bool(curve.axis_legend)

    # Calcul de la reservation basse (proportion de la hauteur de figure)
    bottom_reserve = 0.06  # espace minimal (footer + watermark)
    if has_summary:
        bottom_reserve += 0.14
    if has_axis_legend:
        bottom_reserve += 0.03 + 0.025 * len(curve.axis_legend)

    if has_summary:
        # Panneau resume critique (encadre gris clair, texte serifs)
        summary_text = _wrap_text(curve.critical_summary, width=115)
        y_position = bottom_reserve - 0.05
        fig.text(
            0.5, y_position, summary_text,
            ha="center", va="top", fontsize=8,
            color="#333333",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f4f4f8",
                      ec="#666666", lw=0.6, alpha=0.95),
            wrap=True,
        )

    if has_axis_legend:
        # Legende des axes en petit texte, alignee a gauche
        legend_lines = [f"  {k} : {v}" for k, v in curve.axis_legend.items()]
        legend_text = "Legende des axes et series :\n" + "\n".join(legend_lines)
        y_legend = 0.045 + (0.02 if has_summary else 0)
        fig.text(
            0.015, y_legend, legend_text,
            ha="left", va="bottom", fontsize=7,
            color="#555555", family="monospace",
        )

    # Footer scientifique (formule + timestamp)
    footer = f"Formule : {curve.formula}    |    Genere le : {curve.generated_at[:19]}Z"
    fig.text(0.5, 0.012, footer, ha="center", fontsize=7,
             style="italic", color="#555555")
    # Watermark Gabriel
    fig.text(0.99, 0.012, "Gabriel Multi-Loop Agent  -  Methode Spectrale Savard",
             ha="right", fontsize=6.5, color="#888888", style="italic")

    plt.tight_layout(rect=[0, bottom_reserve, 1, 1])
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def _wrap_text(text: str, width: int = 115) -> str:
    """Wrap un texte pour l'affichage matplotlib (respecte les phrases)."""
    import textwrap
    # Preserve les newlines explicites
    lines: list[str] = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(lines)
