import math
import heapq
from collections import deque


# ─────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────

class CityMap:
    """
    Stores the road network and city coordinates.
    Provides neighbour generation, goal testing, and heuristic computation.
    """

    def __init__(self):
        # adjacency list: {city: [(neighbour, distance), ...]}
        self.roads = {}
        # positions: {city: (x, y)}
        self.positions = {}

    # ── Loaders ──────────────────────────────

    def load_roads(self, filename: str) -> None:
        """Parse roads.txt and populate the adjacency list."""
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("city"):   # skip header/blank
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                city1, city2, dist = parts[0], parts[1], int(parts[2])
                self._add_road(city1, city2, dist)

    def _add_road(self, city1: str, city2: str, dist: int) -> None:
        """Add a bidirectional edge between city1 and city2."""
        # Normalise "Triesta" → "Trieste" (typo in the data file)
        city1 = self._normalise(city1)
        city2 = self._normalise(city2)
        self.roads.setdefault(city1, []).append((city2, dist))
        self.roads.setdefault(city2, []).append((city1, dist))

    def load_positions(self, filename: str) -> None:
        """Parse positions.txt and store (x, y) per city."""
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("city"):
                    continue
                parts = line.split()
                if len(parts) < 3:
                    continue
                city = self._normalise(parts[0])
                self.positions[city] = (float(parts[1]), float(parts[2]))

    @staticmethod
    def _normalise(name: str) -> str:
        """Fix known typos / capitalisation issues in the data files."""
        fixes = {"Triesta": "Trieste"}
        return fixes.get(name, name)

    # ── Domain methods ────────────────────────

    def neighbours(self, city: str):
        """Return list of (neighbour, distance) for a given city."""
        return self.roads.get(city, [])

    def is_goal(self, city: str, goal: str) -> bool:
        """Return True when city matches the goal."""
        return city == goal

    def heuristic(self, city: str, goal: str, factor: float = 1.0) -> float:
        """
        Euclidean (air) distance between city and goal, scaled by factor.
        factor=1.0  → admissible heuristic (standard A*)
        factor=0.5  → under-estimate (more nodes, optimal)
        factor=1.5  → over-estimate (fewer nodes, may be sub-optimal)
        """
        if city not in self.positions or goal not in self.positions:
            return 0.0
        x1, y1 = self.positions[city]
        x2, y2 = self.positions[goal]
        return factor * math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def cities(self):
        """Return a sorted list of all known city names."""
        return sorted(self.roads.keys())


# ─────────────────────────────────────────────
# NODE
# ─────────────────────────────────────────────

class Node:
    """A single node in the search tree."""

    def __init__(self, city: str, parent=None, cost: int = 0):
        self.city = city        # current city name
        self.parent = parent    # parent Node (None for root)
        self.cost = cost        # cumulative path cost from start

    def path(self) -> list:
        """Trace back through parents to reconstruct the full city path."""
        node, route = self, []
        while node:
            route.append(node.city)
            node = node.parent
        return list(reversed(route))

    # Allow nodes to be compared by city name (for visited sets)
    def __eq__(self, other):
        return isinstance(other, Node) and self.city == other.city

    def __hash__(self):
        return hash(self.city)


# ─────────────────────────────────────────────
# SEARCH ALGORITHMS
# ─────────────────────────────────────────────

def depth_first_search(city_map: CityMap, start: str, goal: str):
    """
    Depth-First Search (DFS).
    Uses a LIFO stack; explores as deep as possible before backtracking.
    Not guaranteed to find the shortest path.
    Returns: (nodes_expanded, path, cost)
    """
    stack = [Node(start)]           # LIFO stack
    visited = set()                 # explored cities
    nodes_expanded = 0

    while stack:
        node = stack.pop()

        if node.city in visited:
            continue
        visited.add(node.city)
        nodes_expanded += 1

        if city_map.is_goal(node.city, goal):
            return nodes_expanded, node.path(), node.cost

        # Push neighbours in reverse order so leftmost is explored first
        for neighbour, dist in reversed(city_map.neighbours(node.city)):
            if neighbour not in visited:
                stack.append(Node(neighbour, node, node.cost + dist))

    return nodes_expanded, [], float("inf")   # no path found


def breadth_first_search(city_map: CityMap, start: str, goal: str):
    """
    Breadth-First Search (BFS).
    Uses a FIFO queue; explores level by level.
    Guaranteed to find the path with fewest edges (not necessarily cheapest).
    Returns: (nodes_expanded, path, cost)
    """
    queue = deque([Node(start)])    # FIFO queue
    visited = set()
    nodes_expanded = 0

    while queue:
        node = queue.popleft()

        if node.city in visited:
            continue
        visited.add(node.city)
        nodes_expanded += 1

        if city_map.is_goal(node.city, goal):
            return nodes_expanded, node.path(), node.cost

        for neighbour, dist in city_map.neighbours(node.city):
            if neighbour not in visited:
                queue.append(Node(neighbour, node, node.cost + dist))

    return nodes_expanded, [], float("inf")


def iterative_deepening_search(city_map: CityMap, start: str, goal: str):
    """
    Iterative Deepening Search (IDS).
    Combines DFS's space efficiency with BFS's completeness by repeatedly
    running depth-limited DFS with increasing depth limits.
    Returns: (nodes_expanded, path, cost)
    """
    total_expanded = 0

    def depth_limited_dfs(node, depth_limit, visited_on_path):
        """Recursive DLS; returns (found_node, expanded_count)."""
        nonlocal total_expanded
        total_expanded += 1

        if city_map.is_goal(node.city, goal):
            return node

        if depth_limit == 0:
            return None

        visited_on_path.add(node.city)
        for neighbour, dist in city_map.neighbours(node.city):
            if neighbour not in visited_on_path:
                child = Node(neighbour, node, node.cost + dist)
                result = depth_limited_dfs(child, depth_limit - 1, visited_on_path)
                if result:
                    return result
        visited_on_path.discard(node.city)
        return None

    # Increase the depth limit until a solution is found
    for limit in range(len(city_map.cities()) + 1):
        result = depth_limited_dfs(Node(start), limit, set())
        if result:
            return total_expanded, result.path(), result.cost

    return total_expanded, [], float("inf")


def uniform_cost_search(city_map: CityMap, start: str, goal: str):
    """
    Uniform Cost Search (UCS / Dijkstra).
    Expands the node with the lowest cumulative path cost first.
    Guaranteed to find the optimal (cheapest) path.
    Returns: (nodes_expanded, path, cost)
    """
    # Priority queue entries: (cost, tie_breaker, node)
    counter = 0
    pq = [(0, counter, Node(start))]
    visited = set()
    nodes_expanded = 0

    while pq:
        cost, _, node = heapq.heappop(pq)

        if node.city in visited:
            continue
        visited.add(node.city)
        nodes_expanded += 1

        if city_map.is_goal(node.city, goal):
            return nodes_expanded, node.path(), node.cost

        for neighbour, dist in city_map.neighbours(node.city):
            if neighbour not in visited:
                counter += 1
                child = Node(neighbour, node, node.cost + dist)
                heapq.heappush(pq, (child.cost, counter, child))

    return nodes_expanded, [], float("inf")


def greedy_search(city_map: CityMap, start: str, goal: str, factor: float = 1.0):
    """
    Greedy Best-First Search.
    Expands the node that appears closest to the goal using the heuristic.
    Fast but not guaranteed to find an optimal path.
    Returns: (nodes_expanded, path, cost)
    """
    counter = 0
    h0 = city_map.heuristic(start, goal, factor)
    pq = [(h0, counter, Node(start))]
    visited = set()
    nodes_expanded = 0

    while pq:
        _, _, node = heapq.heappop(pq)

        if node.city in visited:
            continue
        visited.add(node.city)
        nodes_expanded += 1

        if city_map.is_goal(node.city, goal):
            return nodes_expanded, node.path(), node.cost

        for neighbour, dist in city_map.neighbours(node.city):
            if neighbour not in visited:
                counter += 1
                h = city_map.heuristic(neighbour, goal, factor)
                child = Node(neighbour, node, node.cost + dist)
                heapq.heappush(pq, (h, counter, child))

    return nodes_expanded, [], float("inf")


def astar_search(city_map: CityMap, start: str, goal: str, factor: float = 1.0):
    """
    A* Search.
    Combines actual cost g(n) with heuristic estimate h(n): f(n) = g(n) + h(n).
    With factor=1.0 (admissible heuristic), it is guaranteed to find the
    optimal solution. factor<1 may expand more nodes; factor>1 may be faster
    but sacrifice optimality.
    Returns: (nodes_expanded, path, cost)
    """
    counter = 0
    g0 = 0
    h0 = city_map.heuristic(start, goal, factor)
    pq = [(g0 + h0, counter, Node(start))]
    visited = set()
    nodes_expanded = 0

    while pq:
        f, _, node = heapq.heappop(pq)

        if node.city in visited:
            continue
        visited.add(node.city)
        nodes_expanded += 1

        if city_map.is_goal(node.city, goal):
            return nodes_expanded, node.path(), node.cost

        for neighbour, dist in city_map.neighbours(node.city):
            if neighbour not in visited:
                counter += 1
                child = Node(neighbour, node, node.cost + dist)
                h = city_map.heuristic(neighbour, goal, factor)
                heapq.heappush(pq, (child.cost + h, counter, child))

    return nodes_expanded, [], float("inf")


# ─────────────────────────────────────────────
# RESULT FORMATTING
# ─────────────────────────────────────────────

def format_result(nodes_expanded: int, path: list, cost) -> str:
    """
    Return a result string in the assignment format:
      (nodes_expanded  cost  city1 city2 ... cityN)
    """
    if not path:
        return "(No path found)"
    cities_str = " ".join(path)
    cost_str = str(cost) if cost != float("inf") else "∞"
    return f"({nodes_expanded}  {cost_str}  {cities_str})"


# ─────────────────────────────────────────────
# USER INTERFACE
# ─────────────────────────────────────────────

ALGORITHMS = {
    "1": ("Depth-First Search",       depth_first_search),
    "2": ("Breadth-First Search",     breadth_first_search),
    "3": ("Iterative Deepening",      iterative_deepening_search),
    "4": ("Uniform Cost Search",      uniform_cost_search),
    "5": ("Greedy Best-First Search", greedy_search),
    "6": ("A* Search",                astar_search),
}


def run_single(city_map: CityMap, start: str, goal: str,
               algo_key: str, factor: float = 1.0):
    """Run one algorithm and return (name, nodes_expanded, path, cost)."""
    name, fn = ALGORITHMS[algo_key]
    if algo_key in ("5", "6"):          # heuristic-based algorithms
        nodes, path, cost = fn(city_map, start, goal, factor)
    else:
        nodes, path, cost = fn(city_map, start, goal)
    return name, nodes, path, cost


def print_result(name: str, nodes: int, path: list, cost):
    """Pretty-print one search result."""
    print(f"\n  Algorithm : {name}")
    print(f"  Result    : {format_result(nodes, path, cost)}")
    if path:
        print(f"  Path      : {' → '.join(path)}")
        print(f"  Cost      : {cost} km")
    print(f"  Nodes exp.: {nodes}")


def interactive_mode(city_map: CityMap):
    """Interactive CLI: ask user for start, goal, strategy, then run."""
    cities = city_map.cities()
    print("\n" + "=" * 60)
    print("  European City Path Finder")
    print("=" * 60)
    print(f"  Available cities: {', '.join(cities)}")

    # ── Get start city ──
    while True:
        start = input("\n  Enter start city: ").strip().title()
        if start in cities:
            break
        print(f"  ⚠  '{start}' not found. Please try again.")

    # ── Get goal city ──
    while True:
        goal = input("  Enter goal city : ").strip().title()
        if goal in cities:
            break
        print(f"  ⚠  '{goal}' not found. Please try again.")

    # ── Choose algorithm ──
    print("\n  Search strategies:")
    for key, (name, _) in ALGORITHMS.items():
        print(f"    {key}. {name}")

    while True:
        choice = input("\n  Enter strategy number (1-6, or 'all'): ").strip().lower()
        if choice == "all" or choice in ALGORITHMS:
            break
        print("  ⚠  Invalid choice. Enter 1-6 or 'all'.")

    # ── Optional heuristic factor ──
    factor = 1.0
    if choice in ("5", "6") or choice == "all":
        print("\n  Heuristic scaling factor options: 0.5 | 1.0 | 1.5")
        raw = input("  Enter factor [default=1.0]: ").strip()
        try:
            factor = float(raw) if raw else 1.0
        except ValueError:
            factor = 1.0
        print(f"  Using heuristic factor: {factor}")

    # ── Run ──
    print(f"\n{'─'*60}")
    print(f"  Searching from {start} to {goal}")
    print(f"{'─'*60}")

    if choice == "all":
        for key in ALGORITHMS:
            name, nodes, path, cost = run_single(city_map, start, goal, key, factor)
            print_result(name, nodes, path, cost)
    else:
        name, nodes, path, cost = run_single(city_map, start, goal, choice, factor)
        print_result(name, nodes, path, cost)

    print()


# ─────────────────────────────────────────────
# ASSIGNMENT RUNS  (parts a, b, c)
# ─────────────────────────────────────────────

def run_assignment(city_map: CityMap):
    """Execute all required assignment experiments and print a report."""

    separator = "=" * 65

    # ── Part (a): Paris → Vienna, all six algorithms ──────────────
    print(f"\n{separator}")
    print("  PART (a) – Paris → Vienna : all six search algorithms")
    print(separator)

    for key in ALGORITHMS:
        name, nodes, path, cost = run_single(city_map, "Paris", "Vienna", key, 1.0)
        print_result(name, nodes, path, cost)

    # ── Part (b): BFS vs DFS node comparisons ─────────────────────
    print(f"\n{separator}")
    print("  PART (b) – BFS vs DFS: node comparison on selected pairs")
    print(separator)

    pairs = [
        ("Amsterdam", "Berlin"),   # short trip – BFS likely wins
        ("Lisbon",    "Warsaw"),   # long diagonal – DFS may dive right
        ("Madrid",    "Vienna"),
        ("Naples",    "Copenhagen"),
    ]

    print(f"\n  {'Pair':<30} {'DFS nodes':>10} {'BFS nodes':>10}  Winner")
    print(f"  {'─'*30} {'─'*10} {'─'*10}  {'─'*6}")
    for s, g in pairs:
        dfs_n, _, dfs_c = depth_first_search(city_map, s, g)
        bfs_n, _, bfs_c = breadth_first_search(city_map, s, g)
        winner = "DFS" if dfs_n < bfs_n else ("BFS" if bfs_n < dfs_n else "TIE")
        pair_str = f"{s} → {g}"
        print(f"  {pair_str:<30} {dfs_n:>10} {bfs_n:>10}  {winner}")

    # ── Part (c): heuristic factor experiment on A* and Greedy ────
    print(f"\n{separator}")
    print("  PART (c) – Heuristic factor (0.5 / 1.0 / 1.5) on Paris→Vienna")
    print(separator)

    for algo_key, label in [("5", "Greedy"), ("6", "A*")]:
        print(f"\n  {label}:")
        print(f"  {'Factor':>8}  {'Nodes':>8}  {'Cost':>8}")
        print(f"  {'─'*8}  {'─'*8}  {'─'*8}")
        for factor in (0.5, 1.0, 1.5):
            _, nodes, path, cost = run_single(
                city_map, "Paris", "Vienna", algo_key, factor)
            cost_str = str(cost) if cost != float("inf") else "∞"
            print(f"  {factor:>8.1f}  {nodes:>8}  {cost_str:>8}")

    print()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    # Load data
    city_map = CityMap()
    city_map.load_roads("roads.txt")
    city_map.load_positions("positions.txt")

    print("\nData loaded successfully.")
    print(f"Cities : {len(city_map.cities())}")
    print(f"Roads  : {sum(len(v) for v in city_map.roads.values()) // 2} unique edges")

    while True:
        print("\n" + "─" * 40)
        print("  Main Menu")
        print("  1. Interactive search")
        print("  2. Run full assignment report")
        print("  3. Quit")
        choice = input("  Your choice: ").strip()

        if choice == "1":
            interactive_mode(city_map)
        elif choice == "2":
            run_assignment(city_map)
        elif choice == "3":
            print("  Goodbye!")
            break
        else:
            print("  Invalid option.")


if __name__ == "__main__":
    main()
