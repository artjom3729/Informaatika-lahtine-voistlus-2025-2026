from math import atan2, pi, cos, sin
from itertools import combinations, permutations
from fractions import Fraction
import sys


def read_points():
    pts = []
    for _ in range(7):
        line = sys.stdin.readline()
        if not line:
            break
        xys = line.strip().split()
        if not xys:
            continue
        x, y = int(xys[0]), int(xys[1])
        pts.append((x, y))
    if len(pts) != 7:
        # If input incomplete, raise
        raise SystemExit("Expected 7 points")
    return pts


def gen_sample_angles(points):
    angles = set()
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        for j in range(i + 1, n):
            x2, y2 = points[j]
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0 and dy == 0:
                continue
            # normal direction is perpendicular to vector (dx,dy)
            ang = atan2(dy, dx) + pi / 2
            # normalize to [0, pi)
            a = ang % pi
            angles.add(a)
    # include 0 angle to be safe
    angles.add(0.0)
    angles = sorted(angles)
    samples = []
    m = len(angles)
    if m == 0:
        return [0.0]
    for i in range(m):
        a1 = angles[i]
        a2 = angles[(i + 1) % m]
        # mid-angle between a1 and a2, watch wrap-around
        if i + 1 < m:
            mid = (a1 + a2) / 2.0
        else:
            # wrap: mid between last and first across pi boundary
            mid = ((a1 + (a2 + pi)) / 2.0) % pi
        samples.append(mid)
    return samples


def generate_partitions(points):
    samples = gen_sample_angles(points)
    partitions = {}
    for theta in samples:
        nx = cos(theta)
        ny = sin(theta)
        projs = [nx * x + ny * y for (x, y) in points]
        s_sorted = sorted(set(projs))
        # thresholds: before first, between each, after last
        thresholds = []
        if len(s_sorted) == 0:
            continue
        thresholds.append(s_sorted[0] - 1.0)
        for k in range(len(s_sorted) - 1):
            thresholds.append((s_sorted[k] + s_sorted[k + 1]) / 2.0)
        thresholds.append(s_sorted[-1] + 1.0)
        for t in thresholds:
            signs = tuple(1 if (p - t) > 0 else -1 for p in projs)
            # ensure no value equals zero (we picked midpoints so safe)
            partitions.setdefault(signs, []).append((theta, t))
    return partitions


def solve_3x3_fraction(mat, rhs):
    # mat is 3x3 of Fractions, rhs length 3
    # use Cramer's rule
    def det3(m):
        return (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )

    D = det3(mat)
    if D == 0:
        return None
    # build matrices with columns replaced
    mA = [
        [rhs[0], mat[0][1], mat[0][2]],
        [rhs[1], mat[1][1], mat[1][2]],
        [rhs[2], mat[2][1], mat[2][2]],
    ]
    mB = [
        [mat[0][0], rhs[0], mat[0][2]],
        [mat[1][0], rhs[1], mat[1][2]],
        [mat[2][0], rhs[2], mat[2][2]],
    ]
    mC = [
        [mat[0][0], mat[0][1], rhs[0]],
        [mat[1][0], mat[1][1], rhs[1]],
        [mat[2][0], mat[2][1], rhs[2]],
    ]
    DA = det3(mA)
    DB = det3(mB)
    DC = det3(mC)
    A = DA / D
    B = DB / D
    C = DC / D
    return (A, B, C)


def find_integer_line_for_partition(points, signs):
    # We look for rational solution of s_i*(A*x_i + B*y_i + C) >= 1
    # try all triples of points as equalities s_i*(...) = 1
    n = len(points)
    candidates = []
    idxs = list(range(n))
    for i, j, k in combinations(idxs, 3):
        mat = []
        rhs = [Fraction(1), Fraction(1), Fraction(1)]
        for idx in (i, j, k):
            s = signs[idx]
            x, y = points[idx]
            mat.append([Fraction(s * x), Fraction(s * y), Fraction(s)])
        sol = solve_3x3_fraction(mat, rhs)
        if sol is None:
            continue
        A, B, C = sol
        # verify all inequalities hold: s*(A*x+B*y+C) >= 1
        ok = True
        for t in range(n):
            s = signs[t]
            x, y = points[t]
            val = s * (A * x + B * y + C)
            if val < Fraction(1):
                ok = False
                break
        if not ok:
            continue
        # convert to integer coefficients by clearing denominators
        den = 1
        for v in (A, B, C):
            den = den * v.denominator // Fraction(den).denominator

        # above line is safe but simpler compute lcm
        def lcm(a, b):
            from math import gcd

            return a // gcd(a, b) * b

        den = 1
        for v in (A, B, C):
            den = lcm(den, v.denominator)
        Ai = int(A * den)
        Bi = int(B * den)
        Ci = int(C * den)
        # normalize sign (not necessary) but keep small
        if Ai == 0 and Bi == 0:
            continue
        candidates.append((Ai, Bi, Ci))
        # We only need a few candidates; collecting many is unnecessary
        if len(candidates) >= 6:
            break
    return candidates


def main():
    points = read_points()
    partitions_map = generate_partitions(points)
    partitions = list(partitions_map.keys())
    # For each partition compute integer line candidates
    partition_candidates = {}
    for p in partitions:
        cand = find_integer_line_for_partition(points, p)
        # if none found (rare), we can skip this partition
        if cand:
            partition_candidates[p] = cand
    # Try triple combos
    for p1, p2, p3 in combinations(partition_candidates.keys(), 3):
        # Try all orderings (lines order corresponds to bits order)
        for perm in permutations((p1, p2, p3), 3):
            patterns = []
            for i in range(7):
                pat = (
                    1 if perm[0][i] > 0 else 0,
                    1 if perm[1][i] > 0 else 0,
                    1 if perm[2][i] > 0 else 0,
                )
                patterns.append(pat)
            if len(set(patterns)) != 7:
                continue
            # try combine integer candidates
            for A1, B1, C1 in partition_candidates[perm[0]]:
                for A2, B2, C2 in partition_candidates[perm[1]]:
                    for A3, B3, C3 in partition_candidates[perm[2]]:
                        # final safety check: none of Ai*x+Bi*y+Ci equals zero
                        good = True
                        for idx, (x, y) in enumerate(points):
                            v1 = A1 * x + B1 * y + C1
                            v2 = A2 * x + B2 * y + C2
                            v3 = A3 * x + B3 * y + C3
                            if v1 == 0 or v2 == 0 or v3 == 0:
                                good = False
                                break
                        if not good:
                            continue
                        # Signs must match partitions
                        match = True
                        for idx in range(7):
                            s1 = (
                                1
                                if (A1 * points[idx][0] + B1 * points[idx][1] + C1) > 0
                                else -1
                            )
                            s2 = (
                                1
                                if (A2 * points[idx][0] + B2 * points[idx][1] + C2) > 0
                                else -1
                            )
                            s3 = (
                                1
                                if (A3 * points[idx][0] + B3 * points[idx][1] + C3) > 0
                                else -1
                            )
                            if (s1, s2, s3) != (
                                perm[0][idx],
                                perm[1][idx],
                                perm[2][idx],
                            ):
                                match = False
                                break
                        if not match:
                            continue
                        # success
                        print("JAH")
                        print(f"{A1} {B1} {C1}")
                        print(f"{A2} {B2} {C2}")
                        print(f"{A3} {B3} {C3}")
                        return
    print("EI")


if __name__ == "__main__":
    main()
