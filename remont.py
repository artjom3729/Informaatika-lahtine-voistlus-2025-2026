import heapq


# Global distance arrays to avoid reallocation
_dist_cache = []
_visited_cache = []


def dijkstra_optimized(source, target, adj, blocked_nodes, V):
    """
    Ultra-optimized greedy Dijkstra with multiple optimizations:
    1. Reuse memory to avoid allocations
    2. Early termination
    3. Skip outdated entries
    4. Efficient blocking check
    """
    global _dist_cache, _visited_cache

    # Reuse or allocate arrays
    if len(_dist_cache) < V + 1:
        _dist_cache = [float("inf")] * (V + 1)
        _visited_cache = [False] * (V + 1)

    # Reset only needed entries (faster than full reset)
    dist = _dist_cache
    visited = _visited_cache
    for i in range(V + 1):
        dist[i] = float("inf")
        visited[i] = False

    # Priority queue: (distance, node)
    pq = [(0, source)]
    dist[source] = 0

    while pq:
        d, u = heapq.heappop(pq)

        # Skip if already visited (greedy optimization)
        if visited[u]:
            continue
        visited[u] = True

        # Early termination - found target
        if u == target:
            return dist[target]

        # Skip if outdated entry
        if d > dist[u]:
            continue

        # Skip if blocked (but allow source/target)
        if u != source and u != target and u in blocked_nodes:
            continue

        # Relax all edges
        for v, w in adj[u]:
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

    return dist[target]


def solve():
    # Fast input reading
    import sys

    input_data = sys.stdin.read().split()
    idx = 0

    N = int(input_data[idx])
    M = int(input_data[idx + 1])
    Q = int(input_data[idx + 2])
    idx += 3

    # Build adjacency list only (no Floyd-Warshall)
    adj = [[] for _ in range(N + 1)]

    for _ in range(M):
        u = int(input_data[idx])
        v = int(input_data[idx + 1])
        length = int(input_data[idx + 2])
        idx += 3
        adj[u].append((v, length))
        adj[v].append((u, length))

    under_repair = set()
    results = []

    for _ in range(Q):
        op = input_data[idx]
        idx += 1

        if op == "-":
            u = int(input_data[idx])
            idx += 1
            under_repair.add(u)
        elif op == "+":
            u = int(input_data[idx])
            idx += 1
            under_repair.discard(u)
        else:  # op == '?'
            u = int(input_data[idx])
            v = int(input_data[idx + 1])
            idx += 2
            result = dijkstra_optimized(u, v, adj, under_repair, N)
            if result >= float("inf"):
                results.append("-1")
            else:
                results.append(str(int(result)))

    # Fast output
    sys.stdout.write("\n".join(results) + "\n")


if __name__ == "__main__":
    solve()
