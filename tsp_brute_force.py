"""
Brute-Force TSP -- Cagayan de Oro City tourist day tour
========================================================
Performance Innovative Task (Graph Theory): Traveling Salesperson Problem

Problem   : Start at Seda Centrio (A), visit 7 tourist stops (B-H) exactly once,
            and return to A, using the shortest total DRIVING DISTANCE (km).
Graph     : complete DIRECTED graph, 8 vertices, 56 arcs (one-way streets make
            u->v and v->u different), weights in kilometres.
Data      : data/locations.csv           -> the vertices (from Google Maps)
            data/distance_matrix_km.csv  -> the arc weights (from Google Maps,
                                            built by build_dataset.py)
Algorithm : Brute force (exhaustive search). Fix the start A and try every
            ordering of the other n-1 stops: (n-1)! = 7! = 5040 tours.
            Because every possible tour is checked, the best one found is the
            proven optimum for this weight matrix.

Run:   python tsp_brute_force.py
       python tsp_brute_force.py --weights recommended     (sensitivity check)
"""
import argparse
import csv
import itertools
import math
import time
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
MATRIX_FILES = {
    "shortest": DATA / "distance_matrix_km.csv",                 # used for the answer
    "recommended": DATA / "distance_matrix_recommended_km.csv",  # sensitivity check only
}


# ----------------------------------------------------------------------------
# 1. INPUT DATA
# ----------------------------------------------------------------------------
def load_locations(path):
    """Return {label: row} for every vertex in locations.csv."""
    with open(path, encoding="utf-8") as f:
        return {row["label"]: row for row in csv.DictReader(f)}


def load_weight_matrix(path):
    """Return (labels, W) where W[u][v] is the distance in km from u to v (Decimal)."""
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    labels = rows[0][1:]
    W = {}
    for row in rows[1:]:
        u = row[0]
        W[u] = {v: Decimal(x) for v, x in zip(labels, row[1:])}
    return labels, W


# ----------------------------------------------------------------------------
# 2. THE ALGORITHM
# ----------------------------------------------------------------------------
def tour_length(tour, W):
    """Total weight of a closed tour such as ('A','B',...,'H','A')."""
    return sum(W[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))


def brute_force_tsp(labels, W, start, on_new_best=None):
    """
    Exhaustive search over all tours that start and end at `start`.
      step 1: list the other n-1 vertices
      step 2: generate every permutation of them  -> (n-1)! tours
      step 3: compute the length of each tour
      step 4: keep the minimum (all ties are kept, too)
    Returns (best_length, best_tours, all_results).
    """
    others = [v for v in labels if v != start]
    best_length, best_tours, all_results = None, [], []

    for number, order in enumerate(itertools.permutations(others), start=1):
        tour = (start,) + order + (start,)
        length = tour_length(tour, W)
        all_results.append((tour, length))

        if best_length is None or length < best_length:
            best_length, best_tours = length, [tour]
            if on_new_best:
                on_new_best(number, tour, length)
        elif length == best_length:
            best_tours.append(tour)

    return best_length, best_tours, all_results


# ----------------------------------------------------------------------------
# 3. CHECKING THE ANSWER
# ----------------------------------------------------------------------------
def verify_tour(tour, labels, start):
    """Closed tour that visits every non-start vertex exactly once."""
    stops = tour[1:-1]
    checks = {
        "starts at the start vertex": tour[0] == start,
        "ends at the start vertex": tour[-1] == start,
        "visits n-1 stops": len(stops) == len(labels) - 1,
        "no stop is repeated": len(set(stops)) == len(stops),
        "every stop is included": set(stops) == set(labels) - {start},
    }
    return checks


# ----------------------------------------------------------------------------
# 4. PRINTING HELPERS
# ----------------------------------------------------------------------------
def arrow(tour):
    return " -> ".join(tour)


def print_matrix(labels, W):
    print("        to:" + "".join(f"{v:>8}" for v in labels))
    for u in labels:
        print(f"  from {u}   " + "".join(f"{'-':>8}" if u == v else f"{W[u][v]:>8.2f}" for v in labels))


def print_leg_table(tour, W, locations):
    print(f"  {'Leg':>3}  {'From':<38} {'To':<38} {'km':>6}  {'Running total':>13}")
    total = Decimal(0)
    for i in range(len(tour) - 1):
        u, v = tour[i], tour[i + 1]
        total += W[u][v]
        print(f"  {i + 1:>3}  {u + ' ' + locations[u]['name']:<38} {v + ' ' + locations[v]['name']:<38}"
              f" {W[u][v]:>6.2f}  {total:>13.2f}")
    return total


def line(char="="):
    print(char * 108)


# ----------------------------------------------------------------------------
# 5. MAIN PROGRAM
# ----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Brute-force TSP for a Cagayan de Oro tourist day tour")
    parser.add_argument("--weights", choices=MATRIX_FILES, default="shortest",
                        help="which Google Maps distance to use as the arc weight")
    parser.add_argument("--start", default="A", help="start/end vertex (default A = Seda Centrio)")
    parser.add_argument("--show", type=int, default=5, help="how many of the first tours to print in full")
    args = parser.parse_args()

    locations = load_locations(DATA / "locations.csv")
    labels, W = load_weight_matrix(MATRIX_FILES[args.weights])
    n = len(labels)

    line()
    print("BRUTE-FORCE TSP  |  Cagayan de Oro City tourist day tour  |  objective: minimise total driving distance (km)")
    line()

    print("\nINPUT 1 - Vertices (Google Maps places)")
    for v in labels:
        loc = locations[v]
        print(f"  {v}  {loc['name']:<38} {loc['role']:<14} ({float(loc['latitude']):.5f}, {float(loc['longitude']):.5f})")

    print(f"\nINPUT 2 - Weight matrix W[u][v] in km  (file: {MATRIX_FILES[args.weights].relative_to(ROOT)})")
    print("  directed graph: row = FROM, column = TO; W[u][v] and W[v][u] can differ")
    print_matrix(labels, W)

    others = [v for v in labels if v != args.start]
    expected = math.factorial(n - 1)
    print(f"\nALGORITHM - fix start {args.start}; permute the other {n - 1} stops {', '.join(others)}")
    print(f"  number of tours to check = (n-1)! = {n - 1}! = {expected}")

    print(f"\nFirst {args.show} tours, computed edge by edge:")
    for k, order in enumerate(itertools.islice(itertools.permutations(others), args.show), start=1):
        tour = (args.start,) + order + (args.start,)
        terms = " + ".join(f"{W[tour[i]][tour[i + 1]]:.2f}" for i in range(n))
        print(f"  #{k}  {arrow(tour)}\n       = {terms} = {tour_length(tour, W):.2f} km")

    print("\nRunning the exhaustive search... every time a shorter tour is found it is printed:")

    def report(number, tour, length):
        print(f"  tour #{number:>4}: {arrow(tour)}  = {length:6.2f} km   <- new best")

    t0 = time.perf_counter()
    best_length, best_tours, results = brute_force_tsp(labels, W, args.start, on_new_best=report)
    seconds = time.perf_counter() - t0

    line()
    print("RESULT")
    line()
    print(f"  tours evaluated : {len(results)}  (expected (n-1)! = {expected})  ->  "
          f"{'all tours checked' if len(results) == expected else 'COUNT MISMATCH'}")
    print(f"  search time     : {seconds:.3f} s")
    print(f"  shortest length : {best_length:.2f} km")
    print(f"  optimal tour(s) : {len(best_tours)}")
    for t in best_tours:
        print(f"      {arrow(t)}")

    best = best_tours[0]
    print("\nVERIFICATION 1 - is it a valid closed tour?")
    for name, ok in verify_tour(best, labels, args.start).items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("  visit count per stop: " + ", ".join(f"{v}={best[1:-1].count(v)}" for v in others))

    print("\nVERIFICATION 2 - recompute the total from the edge weights, leg by leg")
    total = print_leg_table(best, W, locations)
    print(f"  recomputed total = {total:.2f} km  ->  "
          f"{'matches the search result' if total == best_length else 'DOES NOT MATCH'}")

    ranked = sorted(results, key=lambda r: (r[1], r[0]))
    worst_tour, worst_length = ranked[-1]
    mean_length = sum(r[1] for r in results) / len(results)
    listed = tuple([args.start] + others + [args.start])
    listed_length = tour_length(listed, W)
    print("\nCOMPARISON with other tours (shows what the optimisation gains)")
    print(f"  optimal tour          : {best_length:7.2f} km")
    print(f"  tour in listed order  : {listed_length:7.2f} km   ({arrow(listed)})")
    print(f"  average of all {len(results)}  : {mean_length:7.2f} km")
    print(f"  worst tour            : {worst_length:7.2f} km   ({arrow(worst_tour)})")
    print(f"  saving vs average     : {mean_length - best_length:7.2f} km "
          f"({(mean_length - best_length) / mean_length * 100:.1f}% shorter)")
    rank_of_second = next(r for r in ranked if r[1] > best_length)
    print(f"  next-best length      : {rank_of_second[1]:7.2f} km   ({arrow(rank_of_second[0])})")

    OUTPUT.mkdir(exist_ok=True)
    out_file = OUTPUT / f"all_tours_ranked_{args.weights}.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "tour", "length_km"])
        for i, (tour, length) in enumerate(ranked, start=1):
            w.writerow([i, arrow(tour), f"{length:.2f}"])
    print(f"\n  all {len(results)} tours, sorted by length, saved to {out_file.relative_to(ROOT)}")

    line()
    print("CONCLUSION: brute force compared every possible tour from A, so this tour is the PROVEN OPTIMUM")
    print("            for this weight matrix (Google Maps driving distances retrieved 19 Oct 2026).")
    line()


if __name__ == "__main__":
    main()
