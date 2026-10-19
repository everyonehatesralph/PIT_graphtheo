"""
verify_independently.py
Independent checks of the brute-force answer (not part of the assigned algorithm;
used only as supporting evidence for the optimality claim).

1. Re-derive the weight matrix from the raw Google Maps log and compare it with
   data/distance_matrix_km.csv.
2. Solve the same instance with a DIFFERENT exact method (Held-Karp dynamic
   programming) and confirm it gives the same minimum length.
3. Show the cost of the optimal tour driven in the opposite direction
   (only equal in an undirected graph).
"""
import csv
import itertools
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from tsp_brute_force import load_weight_matrix, tour_length, brute_force_tsp

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def held_karp(labels, W, start):
    """Exact TSP by dynamic programming over subsets (O(n^2 2^n))."""
    others = [v for v in labels if v != start]
    best = {(frozenset([v]), v): (W[start][v], start) for v in others}
    for size in range(2, len(others) + 1):
        for subset in itertools.combinations(others, size):
            S = frozenset(subset)
            for last in subset:
                prev_set = S - {last}
                best[(S, last)] = min((best[(prev_set, p)][0] + W[p][last], p) for p in prev_set)
    full = frozenset(others)
    length, last = min((best[(full, v)][0] + W[v][start], v) for v in others)
    tour, S = [start], full
    while last != start:
        tour.append(last)
        _, prev = best[(S, last)]
        S = S - {last}
        last = prev
    tour.append(start)
    return length, tuple(reversed(tour))


def main():
    before = (DATA / "distance_matrix_km.csv").read_text(encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "build_dataset.py")], check=True, capture_output=True)
    after = (DATA / "distance_matrix_km.csv").read_text(encoding="utf-8")
    print(f"[{'PASS' if before == after else 'FAIL'}] weight matrix re-derived from the raw Google Maps log is identical")

    labels, W = load_weight_matrix(DATA / "distance_matrix_km.csv")
    bf_length, bf_tours, results = brute_force_tsp(labels, W, "A")
    hk_length, hk_tour = held_karp(labels, W, "A")
    print(f"     brute force : {bf_length:.2f} km  {' -> '.join(bf_tours[0])}")
    print(f"     Held-Karp   : {hk_length:.2f} km  {' -> '.join(hk_tour)}")
    print(f"[{'PASS' if bf_length == hk_length and hk_tour in bf_tours else 'FAIL'}] "
          f"a different exact algorithm finds the same optimum")

    lengths = [length for _, length in results]
    print(f"[{'PASS' if min(lengths) == bf_length and lengths.count(bf_length) == len(bf_tours) else 'FAIL'}] "
          f"no tour among all {len(results)} is shorter than {bf_length:.2f} km")

    # Google shows >= 1 km to 0.1 km (true value within +-0.05) and < 1 km in 50 m steps (+-0.025).
    def rounding_bound(u, v):
        return Decimal("0.05") if W[u][v] >= 1 else Decimal("0.025")

    best = bf_tours[0]
    best_arcs = {(best[i], best[i + 1]) for i in range(len(best) - 1)}
    fragile = []
    for tour, length in results:
        arcs = {(tour[i], tour[i + 1]) for i in range(len(tour) - 1)}
        if arcs == best_arcs:
            continue
        worst_case_error = sum(rounding_bound(u, v) for (u, v) in arcs ^ best_arcs)
        if length - bf_length <= worst_case_error:
            fragile.append((tour, length, worst_case_error))
    print(f"[{'PASS' if not fragile else 'NOTE'}] rounding check: "
          + ("for every other tour, the gap to the optimum is larger than the largest possible rounding "
             "error on the arcs where the two tours differ" if not fragile else
             f"{len(fragile)} tour(s) could tie or beat the optimum if Google's rounded distances were exact:"))
    for tour, length, err in sorted(fragile, key=lambda f: f[1])[:10]:
        print(f"     {' -> '.join(tour)} = {length:.2f} km (gap {length - bf_length:.2f} <= max rounding {err:.3f})")

    reverse = tuple(reversed(best))
    print(f"     same loop, opposite direction: {' -> '.join(reverse)} = {tour_length(reverse, W):.2f} km "
          f"(vs {bf_length:.2f} km) -> direction matters in this directed graph")


if __name__ == "__main__":
    main()
