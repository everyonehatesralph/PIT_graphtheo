"""
build_dataset.py
Turns the raw Google Maps route list (data/raw/google_maps_routes_2026-10-19.txt)
into the edge-weight files used by tsp_brute_force.py.

Edge weight rule (stated in the presentation):
    w(u -> v) = the SHORTEST driving distance among the routes Google Maps
                suggested from u to v (ties -> the one Google ranked higher).

Outputs (all in data/):
    routes_all.csv                       every suggested route, parsed
    edges_used.csv                       the route chosen for each ordered pair
    distance_matrix_km.csv               8 x 8 weight matrix used by the solver
    distance_matrix_recommended_km.csv   Google's top-ranked route instead
                                         (only for the sensitivity check)
"""
import csv
import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "raw" / "google_maps_routes_2026-10-19.txt"

LINE = re.compile(
    r"^(?P<u>[A-H])(?P<v>[A-H])\s*\|\s*(?P<rank>\d+)\s*\|\s*"
    r"(?P<time>(?:\d+ hr )?\d+ min)\s+(?P<dist>[\d.,]+)\s*(?P<unit>km|m)\s+via\s+(?P<via>.*)$"
)
NOTE = re.compile(r"\s+(?=(Fastest route|Best route|Some traffic|Heavy traffic|Light traffic))")


def minutes(text):
    h = re.search(r"(\d+) hr", text)
    m = re.search(r"(\d+) min", text)
    return (int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0)


def to_km(number, unit):
    value = Decimal(number.replace(",", ""))
    return value if unit == "km" else value / 1000


def main():
    labels = [row["label"] for row in csv.DictReader(open(DATA / "locations.csv", encoding="utf-8"))]

    routes = []
    for raw in RAW.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        m = LINE.match(raw.strip())
        if not m:
            raise ValueError(f"Cannot parse line: {raw!r}")
        via, *note = NOTE.split(m["via"], maxsplit=1)
        routes.append({
            "from": m["u"], "to": m["v"], "google_rank": int(m["rank"]),
            "minutes": minutes(m["time"]), "km": to_km(m["dist"], m["unit"]),
            "via": via.strip(), "google_note": (note[-1] if note else "").strip(),
        })

    # every ordered pair (u, v), u != v, must have at least one route
    pairs = {(u, v) for u in labels for v in labels if u != v}
    found = {(r["from"], r["to"]) for r in routes}
    assert found == pairs, f"missing pairs: {sorted(pairs - found)}"

    chosen, recommended = {}, {}
    for (u, v) in sorted(pairs):
        options = sorted((r for r in routes if (r["from"], r["to"]) == (u, v)), key=lambda r: r["google_rank"])
        recommended[(u, v)] = options[0]
        chosen[(u, v)] = min(options, key=lambda r: (r["km"], r["google_rank"]))

    fields = ["from", "to", "google_rank", "minutes", "km", "via", "google_note"]
    with open(DATA / "routes_all.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in routes:
            w.writerow({**r, "km": f"{r['km']:.2f}"})

    with open(DATA / "edges_used.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for key in sorted(chosen):
            r = chosen[key]
            w.writerow({**r, "km": f"{r['km']:.2f}"})

    for name, table in (("distance_matrix_km.csv", chosen),
                        ("distance_matrix_recommended_km.csv", recommended)):
        with open(DATA / name, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["from\\to"] + labels)
            for u in labels:
                w.writerow([u] + ["0.00" if u == v else f"{table[(u, v)]['km']:.2f}" for v in labels])

    asym = sum(1 for (u, v) in pairs if u < v and chosen[(u, v)]["km"] != chosen[(v, u)]["km"])
    print(f"Parsed {len(routes)} suggested routes for {len(pairs)} ordered pairs.")
    print(f"Pairs where w(u->v) != w(v->u): {asym} of {len(pairs) // 2}")
    print("Wrote routes_all.csv, edges_used.csv, distance_matrix_km.csv, distance_matrix_recommended_km.csv")


if __name__ == "__main__":
    main()
