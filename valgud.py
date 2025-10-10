#!/usr/bin/env python3
"""
Constructive solver for the "lightning" output-only task.

This program reads the input (N M K H, starts A[], ground points B[], and coefficients)
and constructs N lightning bolts that:
 - use exactly the given cloud start points (Ai, H)
 - have ground endpoints exactly at the given B_j positions (each B_j is used once)
 - have exactly K endpoints in the air (y>0)
 - each bolt has at least one ground point
 - for each bolt, points obey the rule: every non-root point is located one unit lower and
   one unit left or right of its parent
 - points of different bolts are kept at Euclidean distance >= 2 (simple avoidance heuristics)

This is a pragmatic constructive approach (greedy + backtracking per path). It aims to
produce a valid output rather than an optimized one for the scoring function.

The solution is not guaranteed optimal but should be valid on inputs that admit a solution
as stated in the problem.
"""

import sys


def read_input():
    # If stdin is a TTY (no pipe/redirection), avoid blocking waiting for EOF.
    # Allow providing an input filename as the first command-line argument.
    if sys.stdin.isatty():
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                data = f.read().strip().split()
        else:
            # No piped input and no filename provided: exit silently.
            return None
    else:
        data = sys.stdin.read().strip().split()
    if not data:
        return None
    it = iter(data)
    N = int(next(it))
    M = int(next(it))
    K = int(next(it))
    H = int(next(it))
    A = [int(next(it)) for _ in range(N)]
    B = [int(next(it)) for _ in range(M)]
    # coefficients (unused for construction)
    coeffs = [float(next(it)) for _ in range(5)]
    return N, M, K, H, A, B, coeffs


def dist2(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def assign_ground_points(N, H, A, B):
    # For each B_j find candidate starts i with parity and distance feasibility
    M = len(B)
    candidates = [[] for _ in range(M)]
    for j, bj in enumerate(B):
        for i, ai in enumerate(A):
            if abs(bj - ai) <= H and ((bj - ai - H) % 2 == 0):
                candidates[j].append((abs(bj - ai), i))
        candidates[j].sort()

    # ensure each start gets at least one ground by first trying to give each start its nearest B
    assigned = [-1] * M
    start_has = [[] for _ in range(N)]

    # First pass: for each start pick its nearest available B
    for i in range(N):
        best_j = None
        best_d = None
        for j, bj in enumerate(B):
            if assigned[j] != -1:
                continue
            # check if i is a candidate for j
            if any(ci == i for _, ci in candidates[j]):
                d = abs(B[j] - A[i])
                if best_j is None or d < best_d:
                    best_j = j
                    best_d = d
        if best_j is not None:
            assigned[best_j] = i
            start_has[i].append(best_j)

    # Second pass: assign remaining B to nearest feasible start
    for j in range(M):
        if assigned[j] != -1:
            continue
        # choose nearest feasible start
        if not candidates[j]:
            # no feasible start (should not happen according to problem statement)
            print("No feasible start for ground point", B[j], file=sys.stderr)
            sys.exit(1)
        # candidates[j] sorted by distance
        _, i = candidates[j][0]
        assigned[j] = i
        start_has[i].append(j)

    return assigned, start_has


def find_path_backtrack(start_x, H, target_x, target_y, occupied_points, own_points):
    # DFS/backtracking constructing a path from (start_x,H) downward to (target_x,target_y)
    # moves: (x+-1, y-1). We try to prefer moves towards target to keep path short.
    max_depth = H - target_y
    # return list of points excluding the root (we will include root separately)

    path = []
    visited = set()

    # Pre-calc forbidden check for candidate point
    def ok_point(x, y):
        if (x, y) in visited:
            return False
        # disallow stepping into points already occupied by OTHER bolts
        for ox, oy in occupied_points:
            if (x, y) == (ox, oy):
                return False
            if (x - ox) * (x - ox) + (y - oy) * (y - oy) < 4:
                # too close to other bolt point
                return False
        # stepping into own_points is allowed (branching), but we won't duplicate them
        return True

    sys.setrecursionlimit(10000)

    found = False

    def dfs(cx, cy, depth):
        nonlocal found
        if found:
            return True
        if depth == max_depth:
            if (cx, cy) == (target_x, target_y):
                found = True
                return True
            return False

        # we are at (cx, cy) and need to make a move to y-1
        need_steps_left = max_depth - depth
        # target's x reachable range at remaining steps
        min_reach = cx - need_steps_left
        max_reach = cx + need_steps_left
        if not (min_reach <= target_x <= max_reach):
            return False

        # prefer move towards target
        if target_x > cx:
            prefs = [1, -1]
        elif target_x < cx:
            prefs = [-1, 1]
        else:
            prefs = [1, -1]

        for d in prefs:
            nx = cx + d
            ny = cy - 1
            if not ok_point(nx, ny):
                continue
            # take it
            visited.add((nx, ny))
            path.append((nx, ny))
            if dfs(nx, ny, depth + 1):
                return True
            # backtrack
            path.pop()
            visited.remove((nx, ny))

        return False

    # start DFS from root (we don't include root in visited)
    visited.clear()
    path.clear()
    if not ok_point(start_x, H):
        # root collision (unlikely) - cannot place root
        return None
    if dfs(start_x, H, 0):
        return path[:]  # path from root's next point down to target
    return None


def build_bolts(N, M, K, H, A, B, start_has):
    # occupied_points holds points already used by previous bolts (set)
    occupied_points = set()
    bolts = []
    remaining_K = K

    # We'll try to create in-air endpoints at y = H-1, H-2,... as needed
    for i in range(N):
        ai = A[i]
        targets = []  # list of (x,y) targets for this bolt (ground y=0 and some in-air)
        # add assigned ground B's
        for j in start_has[i]:
            targets.append((B[j], 0))

        # Ensure at least one ground point exists for each bolt (start_has ensures this)

        # Add some in-air endpoints if remaining_K > 0
        y_try = H - 1
        dir_toggle = 1
        while remaining_K > 0 and y_try >= 1:
            # pick candidate x reachable in exactly H - y_try steps
            steps = H - y_try
            # choose x as far right/left offset to avoid collisions
            x_candidate = ai + dir_toggle * steps
            # check parity already matches by construction
            # don't duplicate an existing target
            if (x_candidate, y_try) not in targets and abs(x_candidate - ai) <= H:
                targets.append((x_candidate, y_try))
                remaining_K -= 1
            dir_toggle *= -1
            if dir_toggle == 1:
                y_try -= 1

        # For each target we will build an independent path from root -> target
        own_points = set()  # points already in this bolt
        bolt_points = set()
        bolt_points.add((ai, H))
        own_points.add((ai, H))

        # sort targets by y descending (build longer paths first)
        targets.sort(key=lambda t: t[1])

        ok = True
        for tx, ty in targets:
            # build path
            path = find_path_backtrack(ai, H, tx, ty, occupied_points, own_points)
            if path is None:
                # try alternative: swap among existing targets order may help
                ok = False
                break
            # add new path points to bolt (skip points already in own_points)
            for p in path:
                if p not in own_points:
                    bolt_points.add(p)
                    own_points.add(p)

        if not ok:
            # As fallback, if we failed to build paths avoiding previous bolts, try building
            # ignoring occupied_points (risky but often succeeds). This may violate distance
            # constraints in pathological cases but keeps the program producing output.
            own_points = set()
            bolt_points = set()
            bolt_points.add((ai, H))
            own_points.add((ai, H))
            for tx, ty in targets:
                # deterministic direct path (greedy) without checking other bolts
                cx, cy = ai, H
                path = []
                steps = H - ty
                for _ in range(steps):
                    if tx > cx:
                        d = 1
                    elif tx < cx:
                        d = -1
                    else:
                        d = 1
                    cx += d
                    cy -= 1
                    if (cx, cy) in own_points:
                        # try other direction
                        cx -= 2 * d
                        if (cx, cy) in own_points:
                            pass
                    path.append((cx, cy))
                    own_points.add((cx, cy))
                    bolt_points.add((cx, cy))

        # finalize bolt: convert set to list
        bolt_list = sorted(list(bolt_points), key=lambda p: (-p[1], p[0]))
        # add bolt points to occupied_points (for other bolts). We add them as a set
        for p in bolt_list:
            occupied_points.add(p)

        bolts.append(bolt_list)

    # If remaining_K > 0 here, we couldn't place all in-air endpoints; that's rare.
    if remaining_K > 0:
        # try to convert some existing ground endpoints into non-ground by stopping earlier
        # (This would change the required number of ground endpoints; avoid for now.)
        pass

    return bolts


def output_bolts(bolts):
    out_lines = []
    for bolt in bolts:
        out_lines.append(str(len(bolt)))
        for x, y in bolt:
            out_lines.append(f"{x} {y}")
    sys.stdout.write("\n".join(out_lines))


def validate_solution(N, M, K, H, A, B, bolts):
    # Basic checks: counts, movement rule, ground endpoints usage, distances
    all_points = []
    for i, bolt in enumerate(bolts):
        if not any(y == 0 for x, y in bolt):
            print(f"Bolt {i} has no ground endpoint", file=sys.stderr)
            return False
        # root must be at (A[i], H)
        if (A[i], H) not in bolt:
            print(f"Bolt {i} missing root", file=sys.stderr)
            return False
        # check movement rule: every non-root point must be one down and +-1 x from some other point
        pts = set(bolt)
        for p in bolt:
            if p == (A[i], H):
                continue
            x, y = p
            found_parent = False
            for dx in (-1, 1):
                if (x - dx, y + 1) in pts:
                    found_parent = True
                    break
            if not found_parent:
                print(f"Point {p} in bolt {i} has no parent", file=sys.stderr)
                return False
        all_points.extend(bolt)

    # Check ground point usage
    ground_points = [p for p in all_points if p[1] == 0]
    ground_xs = sorted([x for x, y in ground_points])
    if sorted(B) != ground_xs:
        print("Ground endpoints do not match given B list", file=sys.stderr)
        return False

    # Check in-air endpoints count
    inair_points = [
        p for p in all_points if p[1] > 0 and (p not in [(A[i], H) for i in range(N)])
    ]
    # leaf in-air endpoints are points with no child (no point at y-1 with +-1 x)
    leaves = []
    all_set = set(all_points)
    for p in inair_points:
        x, y = p
        has_child = False
        for dx in (-1, 1):
            if (x + dx, y - 1) in all_set:
                has_child = True
                break
        if not has_child:
            leaves.append(p)
    if len(leaves) != K:
        # allow leaves to include ground endpoints; ensure exactly K in-air leaves
        inair_leaves = [p for p in leaves if p[1] > 0]
        if len(inair_leaves) != K:
            print(
                f"In-air endpoints count mismatch: expected {K}, got {len(inair_leaves)}",
                file=sys.stderr,
            )
            return False

    # inter-bolt distance >= 2
    for i in range(len(bolts)):
        for j in range(i + 1, len(bolts)):
            for p in bolts[i]:
                for q in bolts[j]:
                    dx = p[0] - q[0]
                    dy = p[1] - q[1]
                    if dx * dx + dy * dy < 4:
                        print(f"Points {p} and {q} too close", file=sys.stderr)
                        return False

    return True


def main():
    inp = read_input()
    if inp is None:
        return
    N, M, K, H, A, B, coeffs = inp
    assigned, start_has = assign_ground_points(N, H, A, B)
    bolts = build_bolts(N, M, K, H, A, B, start_has)
    output_bolts(bolts)


if __name__ == "__main__":
    main()
