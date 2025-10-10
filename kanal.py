from collections import defaultdict
import sys


class Fenwick:
    def __init__(self, n):
        self.n = n
        self.bit = [0] * (n + 1)

    def add(self, i, delta):
        i += 1
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def sum(self, i):
        i += 1
        res = 0
        while i > 0:
            res += self.bit[i]
            i -= i & -i
        return res

    def range_sum(self, left, right):
        if right < left:
            return 0
        if left > 0:
            return self.sum(right) - self.sum(left - 1)
        return self.sum(right)


def full_lehmer_decode(wagons, m, n):
    counts = defaultdict(int)
    for val in wagons:
        counts[val] += 1
    canon = []
    for val in sorted(counts.keys()):
        for i in range(counts[val]):
            canon.append((val, i))
    canon_pos = {pair: pos for pos, pair in enumerate(canon)}
    occ = defaultdict(int)
    perm_ids = []
    for val in wagons:
        tie = occ[val]
        occ[val] += 1
        perm_ids.append(canon_pos[(val, tie)])

    fenw = Fenwick(n)
    for i in range(n):
        fenw.add(i, 1)

    lehmer = [0] * n
    for i in range(n):
        x = perm_ids[i]
        smaller = fenw.range_sum(0, x - 1)
        lehmer[i] = smaller
        fenw.add(x, -1)

    perm_index_mod = 0
    for i in range(n):
        perm_index_mod = (perm_index_mod * (n - i) + lehmer[i]) % m
    return perm_index_mod


def main():
    mode = sys.stdin.readline().strip()

    if mode == "ENC":
        m, n = [int(x) for x in sys.stdin.readline().split()]
        v = [int(x) for x in sys.stdin.readline().split()]

        distinct_sorted = sorted(set(v))
        can_map = len(distinct_sorted) >= m
        if can_map:
            map_vals = distinct_sorted[:m]
        else:
            map_vals = []

        positions = defaultdict(list)
        for idx, val in enumerate(v):
            positions[val].append(idx)

        while True:
            line = sys.stdin.readline()
            if not line:
                break
            s = int(line)
            if s == -1:
                break

            if can_map and 0 <= s < m:
                target = map_vals[s]
                first_idx = positions[target][0]
                out = [v[first_idx]]
                for i in range(n):
                    if i == first_idx:
                        continue
                    out.append(v[i])
                print(*out, flush=True)
            else:
                print(*v, flush=True)

    elif mode == "DEC":
        m, n = [int(x) for x in sys.stdin.readline().split()]

        learned = False
        val_to_s = None

        while True:
            print("R", flush=True)
            line = sys.stdin.readline()
            if not line:
                break
            first = int(line)
            if first == -1:
                break

            if not learned:
                wagons = [first]
                for _ in range(n - 1):
                    print("R", flush=True)
                    wagons.append(int(sys.stdin.readline()))
                distinct_sorted = sorted(set(wagons))
                if len(distinct_sorted) >= m:
                    map_vals = distinct_sorted[:m]
                    val_to_s = {map_vals[i]: i for i in range(m)}
                else:
                    val_to_s = None
                learned = True
                if val_to_s and wagons[0] in val_to_s:
                    print(val_to_s[wagons[0]], flush=True)
                else:
                    print(full_lehmer_decode(wagons, m, n), flush=True)
            else:
                if val_to_s and first in val_to_s:
                    print(val_to_s[first], flush=True)
                else:
                    wagons = [first]
                    for _ in range(n - 1):
                        print("R", flush=True)
                        wagons.append(int(sys.stdin.readline()))
                    print(full_lehmer_decode(wagons, m, n), flush=True)

    else:
        pass


if __name__ == "__main__":
    main()
