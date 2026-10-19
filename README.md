# PIT – Brute-Force TSP: Cagayan de Oro tourist day tour

Start at **Seda Centrio (A)**, visit 7 attractions once each, return to A, with minimum total
**driving distance (km)**. Assigned algorithm: **Brute Force** (exhaustive search).

**Result:** `A → C → D → B → G → H → F → E → A` = **63.50 km**. Proven optimal for this data:
all 7! = 5,040 tours were checked. It's the only tour at that length; the next best is 64.05 km.

## Run it

```bash
python tsp_brute_force.py
```

Python 3.8+ with no extra packages (uses `itertools`, `decimal`, `csv`). `make_figures.py` needs `matplotlib`.

| Command | What it does |
|---|---|
| `python tsp_brute_force.py` | **The submission program.** Prints input, first tours, search trace, result, verification, comparison. |
| `python tsp_brute_force.py --weights recommended` | Sensitivity check: uses Google's top-ranked route instead of the shortest one. |
| `python verify_independently.py` | Extra evidence: rebuilds the matrix from the raw log, runs Held–Karp DP, runs the rounding-robustness check. |
| `python build_dataset.py` | Rebuilds the `data/*.csv` files from the raw Google Maps log. |
| `python make_figures.py` | Redraws `figures/*.png`. |

## Dataset (identify this in the submission)

| File | Content |
|---|---|
| `data/locations.csv` | The 8 vertices: label, name, role, Google Maps listing, latitude/longitude |
| `data/distance_matrix_km.csv` | **The input of the program:** 8×8 directed weight matrix in km (row = from, column = to) |
| `data/raw/google_maps_routes_2026-10-19.txt` | Raw log: every route Google Maps suggested for all 56 ordered pairs (155 routes) |
| `data/routes_all.csv` | The same routes, parsed (minutes, km, road names) |
| `data/edges_used.csv` | The route chosen as the weight for each ordered pair |
| `data/distance_matrix_recommended_km.csv` | Alternative matrix (Google's top-ranked route). Used only for the sensitivity check |

**Edge-weight rule:** w(u→v) = the shortest of the driving routes Google Maps suggested from u to v.
Google Maps directions were retrieved on 19 Oct 2026, 7:33–7:47 PM PHT. **Actual data:** the places,
coordinates and route distances. **Assumed:** the choice of start and stops, travel by car, the
weight rule, distances fixed all day, no time windows.

## Before you record or submit — your part

1. **Fill the placeholders** on slide 1: `[Your name]`, `[Course and section]`, `[Instructor]`.
2. **Spot-check 3–4 distances** yourself on Google Maps (e.g. A→C 1.4 km, C→A 1.1 km, B→G 13.1 km).
   Routes can change slightly over time. If one changes, edit `data/raw/…txt`, then rerun `build_dataset.py`.
3. **Record the video (10–15 min)** following [VIDEO_SCRIPT.md](VIDEO_SCRIPT.md), which has every line to say plus the
   VS Code and terminal steps (~13 min).
   On slide 12, screen-record a real run of `python tsp_brute_force.py` in a terminal. A screenshot alone does not count.
4. **AI-assistance disclosure:** reference 7 on the last slide says the code was prepared with AI assistance.
   Edit it to match your course's policy.
5. **Submit:** the video, `tsp_brute_force.py` (plus the helper scripts) and the `data/` folder.

## Caveats about the source paper (Luna-Garcia et al., 2024)

Don't copy its appendix code or cite its Table 2 numbers as evidence:
- Its brute-force code permutes all n cities (n!), not (n−1)! as its own text says. That's harmless but wasteful.
- Its DP path reconstruction returns `[0, 0, …]`, because it looks up keys that never exist.
- Its divide-and-conquer merge can repeat cities.
- Table 2 reports two different "best" values for exact methods on the same 8-city case (DP 2238.43 vs. brute force 1974.37).
- All of its code uses straight-line coordinates, not road distances.
