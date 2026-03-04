# CSCE 3601 – Assignment #1: Searching for Paths

A Python program that finds routes between European cities using six classical AI search algorithms.

---

## Files

| File | Description |
|---|---|
| `search.py` | Main program – all search algorithms and UI |
| `roads.txt` | Road network data (city pairs + distances in km) |
| `positions.txt` | City coordinates (used for the heuristic) |

---

## Requirements

- Python 3.7 or later
- No third-party packages needed (uses only `math`, `heapq`, `collections`)

---

## How to Run

1. Place all three files in the same folder.
2. Open a terminal in that folder and run:

```bash
python search.py
```

> On Mac/Linux use `python3 search.py` if `python` is not found.

3. You will see the main menu:

```
Main Menu
  1. Interactive search
  2. Run full assignment report
  3. Quit
```

- **Option 1** – Enter a start city, goal city, algorithm (1–6 or `all`), and an optional heuristic factor.
- **Option 2** – Automatically runs all required assignment experiments (Parts a, b, c) and prints a full report.

---

## Algorithms

| # | Algorithm | Optimal? | Notes |
|---|---|---|---|
| 1 | Depth-First Search (DFS) | No | Fast but path quality is unpredictable |
| 2 | Breadth-First Search (BFS) | Hop-optimal | Finds fewest-edge path |
| 3 | Iterative Deepening (IDS) | Hop-optimal | Low memory, higher node count |
| 4 | Uniform Cost Search (UCS) | **Yes** | Always finds cheapest path |
| 5 | Greedy Best-First | No | Fewest expansions, uses heuristic only |
| 6 | A\* Search | **Yes** | Best overall — optimal and efficient |

The heuristic used for Greedy and A\* is the **Euclidean (straight-line) distance** between the current city and the goal, optionally scaled by a factor (0.5, 1.0, or 1.5).

---

## Output Format

Results are printed in the following format:

```
(nodes_expanded  cost  city1 city2 ... cityN)
```

Example:

```
(7  520  Amsterdam Hamburg Berlin)
```

---

## Available Cities

Amsterdam, Belgrade, Berlin, Bern, Brussel, Budapest, Copenhagen,
Genoa, Hamburg, Lisbon, Madrid, Munich, Naples, Paris, Prague,
Rome, Trieste, Vienna, Warsaw

---

## Complexity Reference

| Algorithm | Time | Space | Cost-Optimal |
|---|---|---|---|
| DFS | O(b^m) | O(bm) | No |
| BFS | O(b^d) | O(b^d) | Hop-optimal |
| IDS | O(b^d) | O(bd) | Hop-optimal |
| UCS | O(b^(C*/ε)) | O(b^(C*/ε)) | Yes |
| Greedy | O(b^m) | O(b^m) | No |
| A\* | O(b^d) | O(b^d) | Yes (admissible h) |

> `b` = branching factor, `d` = depth of shallowest goal, `m` = max depth, `C*` = optimal cost, `ε` = minimum edge cost.

---

## Example Interactive Session

```
Main Menu
  1. Interactive search
  2. Run full assignment report
  3. Quit
Your choice: 1

European City Path Finder
Available cities: Amsterdam, Belgrade, Berlin, ...

Enter start city: Paris
Enter goal city : Vienna

Search strategies:
  1. Depth-First Search
  2. Breadth-First Search
  3. Iterative Deepening
  4. Uniform Cost Search
  5. Greedy Best-First Search
  6. A* Search
Enter strategy number (1-6, or 'all'): 6

Heuristic scaling factor options: 0.5 | 1.0 | 1.5
Enter factor [default=1.0]: 1.0

Searching from Paris to Vienna
──────────────────────────────────────────────────────────
  Algorithm : A* Search
  Result    : (9  1195  Paris Brussel Amsterdam Munich Vienna)
  Path      : Paris → Brussel → Amsterdam → Munich → Vienna
  Cost      : 1195 km
  Nodes exp.: 9
```

---

## Extending the Map

You can add new cities and roads by editing the two data files directly — no code changes needed.

**`positions.txt`** — add a line per new city:
```
CityName    x-coordinate    y-coordinate
```

**`roads.txt`** — add a line per new road (bidirectional):
```
City1    City2    distance_in_km
```

Both files are tab-separated. City names must be consistent across both files.

---

## Notes

- City names are **case-insensitive** on input (automatically title-cased).
- A typo in the original data file (`Triesta` → `Trieste`) is corrected automatically at load time.
- The heuristic factor only applies to Greedy and A\*. Factor `1.0` is the standard admissible setting. Using `> 1.0` speeds up A\* but may sacrifice optimality.
