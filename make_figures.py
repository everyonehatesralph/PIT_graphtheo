"""
make_figures.py -- draws the figures used in the presentation (saved in figures/).

  fig1_graph_model.png       labeled complete directed graph with all 56 weights
  fig2_optimal_tour.png      the optimal tour found by brute force
  fig3_weight_matrix.png     weight matrix with the 8 arcs of the optimal tour highlighted
  fig4_all_tour_lengths.png  histogram of the lengths of all 5040 tours
  fig5_tour_on_coordinates.png  the optimal tour drawn on the real Google Maps coordinates
"""
import math
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from tsp_brute_force import load_locations, load_weight_matrix, brute_force_tsp, tour_length

ROOT = Path(__file__).resolve().parent
DATA, FIG = ROOT / "data", ROOT / "figures"
FIG.mkdir(exist_ok=True)

INK, MUTED, GRID = "#1f2937", "#6b7280", "#d1d5db"
TOUR, TOUR_LIGHT, START = "#c2410c", "#fde3d3", "#1d4ed8"

# Schematic positions (north is up; the downtown cluster A-E is enlarged so its labels fit)
POS = {
    "D": (-1.0, 7.2), "A": (2.6, 7.6), "E": (6.0, 6.3),
    "B": (-3.0, 4.9), "C": (1.2, 4.5),
    "H": (2.2, -1.6), "F": (8.6, 0.9), "G": (-5.6, -3.4),
}
SHORT = {
    "A": "Seda Centrio\n(start/end)", "B": "St. Augustine\nCathedral", "C": "Museo de Oro",
    "D": "Plaza Divisoria", "E": "Limketkai\nCenter", "F": "Mapawa\nNature Park",
    "G": "Macahambus\nCave & Gorge", "H": "Amaya View",
}
LABEL_OFFSET = {"A": (0, 0.95), "B": (-1.9, 0.0), "C": (0, -1.0), "D": (0, 0.95), "E": (0.3, 0.95),
                "F": (0, -1.05), "G": (0, -1.05), "H": (0, -1.05)}

locations = load_locations(DATA / "locations.csv")
labels, W = load_weight_matrix(DATA / "distance_matrix_km.csv")
best_length, best_tours, results = brute_force_tsp(labels, W, "A")
BEST = best_tours[0]
BEST_ARCS = {(BEST[i], BEST[i + 1]) for i in range(len(BEST) - 1)}


def km(x):
    return f"{x:.2f}".rstrip("0").rstrip(".") if x % 1 else f"{x:.0f}"


def draw_nodes(ax, highlight_start=True):
    for v, (x, y) in POS.items():
        color = START if (v == "A" and highlight_start) else INK
        ax.scatter(x, y, s=900, color="white", edgecolors=color, linewidths=2.5, zorder=5)
        ax.text(x, y, v, ha="center", va="center", fontsize=15, fontweight="bold", color=color, zorder=6)
        dx, dy = LABEL_OFFSET[v]
        ax.text(x + dx, y + dy, SHORT[v], ha="center", va="center", fontsize=9.5, color=MUTED, zorder=6,
                linespacing=1.1)


def setup(ax, title):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-8.2, 11.0)
    ax.set_ylim(-7.4, 9.4)
    ax.set_title(title, fontsize=15, fontweight="bold", color=INK, loc="left", pad=12)


def label_position(u, v, t=0.5, push=0.0):
    (x1, y1), (x2, y2) = POS[u], POS[v]
    x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
    length = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / length, (x2 - x1) / length
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if angle > 90:
        angle -= 180
    if angle < -90:
        angle += 180
    return x + nx * push, y + ny * push, angle


# Where to put each pair's label along its edge (0..1 from the alphabetically first vertex)
LABEL_T = {("A", "B"): 0.32, ("A", "C"): 0.42, ("A", "D"): 0.5, ("A", "E"): 0.5, ("B", "C"): 0.5,
           ("B", "D"): 0.5, ("B", "E"): 0.22, ("C", "D"): 0.45, ("C", "E"): 0.62, ("D", "E"): 0.68,
           ("A", "F"): 0.62, ("A", "G"): 0.72, ("A", "H"): 0.62, ("B", "F"): 0.75, ("B", "G"): 0.45,
           ("B", "H"): 0.72, ("C", "F"): 0.55, ("C", "G"): 0.55, ("C", "H"): 0.42, ("D", "F"): 0.45,
           ("D", "G"): 0.33, ("D", "H"): 0.3, ("E", "F"): 0.42, ("E", "G"): 0.28, ("E", "H"): 0.55,
           ("F", "G"): 0.22, ("F", "H"): 0.7, ("G", "H"): 0.5}


def fig1():
    fig, ax = plt.subplots(figsize=(14, 11))
    setup(ax, "Weighted directed graph: 8 vertices, 56 arcs (km, Google Maps driving distance)")
    for u, v in LABEL_T:
        (x1, y1), (x2, y2) = POS[u], POS[v]
        ax.plot([x1, x2], [y1, y2], color=GRID, lw=1.3, zorder=1)
        x, y, ang = label_position(u, v, LABEL_T[(u, v)])
        ax.text(x, y, f"{km(W[u][v])} | {km(W[v][u])}", fontsize=8.6, color=INK, ha="center", va="center",
                rotation=ang, rotation_mode="anchor", zorder=3,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.95))
    draw_nodes(ax)
    ax.text(-8.0, -7.2,
            "How to read an edge label  \"x | y\"  on the line between u and v (u comes first in the alphabet):\n"
            "x = w(u -> v),  y = w(v -> u).   Example: A-C reads \"1.4 | 1.1\": A -> C = 1.40 km but C -> A = 1.10 km.\n"
            "Source: Google Maps driving directions, shortest suggested route, retrieved 19 Oct 2026. "
            "Layout is schematic (downtown enlarged).",
            fontsize=9.5, color=MUTED, va="bottom")
    fig.savefig(FIG / "fig1_graph_model.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def arc(ax, u, v, color, lw, rad=0.0, z=4):
    p = FancyArrowPatch(POS[u], POS[v], arrowstyle="-|>", mutation_scale=22, color=color, lw=lw,
                        shrinkA=19, shrinkB=19, connectionstyle=f"arc3,rad={rad}", zorder=z)
    ax.add_patch(p)


# (position along the arc, sideways push) for the crowded downtown legs
LEG_LABEL = {1: (0.3, 0.0), 2: (0.62, 0.0), 3: (0.7, -0.35), 8: (0.5, -0.45)}


def fig2():
    fig, ax = plt.subplots(figsize=(14, 11))
    setup(ax, f"Optimal tour found by brute force: {best_length:.2f} km")
    for u, v in LABEL_T:
        (x1, y1), (x2, y2) = POS[u], POS[v]
        ax.plot([x1, x2], [y1, y2], color="#eef0f3", lw=1.0, zorder=1)
    total = Decimal(0)
    for i in range(len(BEST) - 1):
        u, v = BEST[i], BEST[i + 1]
        total += W[u][v]
        arc(ax, u, v, TOUR, 3.2)
        x, y, _ = label_position(u, v, *LEG_LABEL.get(i + 1, (0.5, 0.0)))
        ax.text(x, y, f"leg {i + 1}: {km(W[u][v])} km", fontsize=10, color=TOUR, fontweight="bold",
                ha="center", va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=TOUR, lw=1))
    draw_nodes(ax)
    ax.text(-8.0, -7.2, "Tour:  " + "  ->  ".join(BEST) + f"      total = {total:.2f} km\n"
            "Each of the 7 stops is visited exactly once; the tour starts and ends at A.",
            fontsize=11, color=INK, va="bottom")
    fig.savefig(FIG / "fig2_optimal_tour.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig3():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.axis("off")
    cells = [[("-" if u == v else f"{W[u][v]:.2f}") for v in labels] for u in labels]
    colours = [[(TOUR_LIGHT if (u, v) in BEST_ARCS else ("#f3f4f6" if u == v else "white")) for v in labels]
               for u in labels]
    rows = [f"{u}  {locations[u]['name'].split(' (')[0]}" for u in labels]
    table = ax.table(cellText=cells, cellColours=colours, rowLabels=rows,
                     colLabels=[f"to {v}" for v in labels], loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.9)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0 or c == -1:
            cell.set_text_props(fontweight="bold", color=INK)
        if r > 0 and c >= 0 and (labels[r - 1], labels[c]) in BEST_ARCS:
            cell.set_text_props(fontweight="bold", color=TOUR)
    ax.set_title("Weight matrix W[from][to] in km  (shaded = the 8 arcs of the optimal tour)",
                 fontsize=13, fontweight="bold", color=INK, loc="left")
    fig.savefig(FIG / "fig3_weight_matrix.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig4():
    lengths = [float(l) for _, l in results]
    mean = sum(lengths) / len(lengths)
    fig, ax = plt.subplots(figsize=(11, 5.4))
    lo, hi = math.floor(min(lengths)), math.ceil(max(lengths))
    ax.hist(lengths, bins=[lo + 0.5 * k for k in range(int((hi - lo) / 0.5) + 1)], color="#9ca3af",
            edgecolor="white")
    ax.axvline(float(best_length), color=TOUR, lw=2.5)
    ax.axvline(mean, color=INK, lw=1.5, ls="--")
    ax.text(float(best_length) + 0.2, ax.get_ylim()[1] * 0.92, f"optimal\n{best_length:.2f} km",
            color=TOUR, fontsize=11, fontweight="bold", va="top")
    ax.text(mean + 0.2, ax.get_ylim()[1] * 0.92, f"average\n{mean:.2f} km", color=INK, fontsize=11, va="top")
    ax.set_xlabel("tour length (km)", fontsize=11)
    ax.set_ylabel("number of tours", fontsize=11)
    ax.set_title(f"Brute force checked all {len(lengths)} tours; exactly one has the minimum length",
                 fontsize=13, fontweight="bold", color=INK, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(FIG / "fig4_all_tour_lengths.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig5():
    coords = {v: (float(locations[v]["longitude"]), float(locations[v]["latitude"])) for v in labels}
    fig, ax = plt.subplots(figsize=(11, 9))
    for i in range(len(BEST) - 1):
        u, v = BEST[i], BEST[i + 1]
        ax.annotate("", xy=coords[v], xytext=coords[u],
                    arrowprops=dict(arrowstyle="-|>", color=TOUR, lw=2.2, shrinkA=7, shrinkB=7))
    for v, (x, y) in coords.items():
        ax.scatter(x, y, s=120, color=START if v == "A" else INK, zorder=5)
    far = {"F": (8, -14), "G": (8, -4), "H": (10, -4)}
    for v in ("F", "G", "H"):
        ax.annotate(f"{v}  {locations[v]['name']}", coords[v], xytext=far[v], textcoords="offset points",
                    fontsize=10, color=INK)
    ax.annotate("A-E: downtown cluster\n(see schematic graph)", coords["C"], xytext=(-150, 28),
                textcoords="offset points", fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("A  Seda Centrio (start/end)", coords["A"], xytext=(10, 6), textcoords="offset points",
                fontsize=10, color=START, fontweight="bold")
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.set_xlabel("longitude (deg E)")
    ax.set_ylabel("latitude (deg N)")
    ax.set_aspect(1 / math.cos(math.radians(8.45)))
    ax.grid(color="#eef0f3")
    ax.set_title("Optimal tour on the real Google Maps coordinates (straight lines; roads are longer)",
                 fontsize=13, fontweight="bold", color=INK, loc="left")
    fig.savefig(FIG / "fig5_tour_on_coordinates.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5):
        f()
        print("saved", f.__doc__ or f.__name__)
    print("figures written to", FIG)
