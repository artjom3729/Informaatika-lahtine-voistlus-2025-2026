import sys

# Offline reverse processing + incremental Floyd-Warshall
# Problem constraints: N <= 350. We'll keep Python-optimized O(N^3) overall approach.

INF = 10**30


def main():
    data = sys.stdin.buffer.read().split()
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    q = int(next(it))

    # initialize distance matrix
    dist = [[INF] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dist[i][i] = 0

    # read edges (keep only minimum for each pair)
    for _ in range(m):
        u = int(next(it))
        v = int(next(it))
        w = int(next(it))
        if w < dist[u][v]:
            dist[u][v] = w
            dist[v][u] = w

    # Read queries and track node activation state
    queries = []  # store tuples: (typ, u, v?) typ: b'?', b'-', b'+'
    blocked = [False] * (n + 1)
    # For each node track whether it is currently blocked at the end
    # Initially no nodes are blocked; apply queries in order to find final state
    for _ in range(q):
        typ = next(it)
        if typ == b"-" or typ == b"+":
            u = int(next(it))
            queries.append((typ, u))
            if typ == b"-":
                blocked[u] = True
            else:
                blocked[u] = False
        else:
            u = int(next(it))
            v = int(next(it))
            queries.append((typ, u, v))

    # We'll process queries in reverse. In reverse, '-' becomes 'activate' node u
    # We'll maintain a boolean active[] where active[node] == True means node is available
    active = [False] * (n + 1)
    # Initially, a node is active iff it is NOT blocked at the end
    for i in range(1, n + 1):
        active[i] = not blocked[i]

    # We'll maintain answers for '?' queries in reverse order
    answers_rev = []

    # Micro-optimizations: local binds
    n1 = n
    dist_local = dist
    active_local = active

    # Helper: do FW update with new node k (1-based index)
    def activate_node(k):
        # activate k
        active_local[k] = True
        dk = dist_local[k]
        # local binds
        for i in range(1, n1 + 1):
            if not active_local[i]:
                continue
            dik = dist_local[i][k]
            if dik >= INF:
                continue
            row_i = dist_local[i]
            # try to relax using k
            # inline inner loop
            for j in range(1, n1 + 1):
                if not active_local[j]:
                    continue
                val = dik + dk[j]
                if val < row_i[j]:
                    row_i[j] = val

    # Process queries in reverse order
    for qitem in reversed(queries):
        if qitem[0] == b"?":
            _, u, v = qitem
            # if both u and v active, read dist[u][v], else unreachable
            if active_local[u] and active_local[v]:
                d = dist_local[u][v]
                answers_rev.append(-1 if d >= INF else d)
            else:
                answers_rev.append(-1)
        else:
            typ = qitem[0]
            u = qitem[1]
            if typ == b"+":
                # in forward: '+' meant unblock (node becomes active); in reverse this is 'deactivate'
                # so in reverse we must deactivate u
                active_local[u] = False
            else:
                # typ == b'-' in forward: node was blocked at that moment; in reverse this is activation
                # activate u and run FW update
                activate_node(u)

    # outputs are answers_rev reversed
    out = []
    for x in reversed(answers_rev):
        out.append(str(x))

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
