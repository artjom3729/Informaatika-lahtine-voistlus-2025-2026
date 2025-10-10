#!/usr/bin/env python3
import sys


def round_to_5(cents: int) -> int:
    r = cents % 5
    if r in (1, 2):
        return cents - r
    if r in (3, 4):
        return cents + (5 - r)
    return cents


def main():
    # Read first line (N) and then N lines of items using input(), so the
    # program works interactively without needing EOF.
    try:
        line = input().strip()
    except EOFError:
        return
    if not line:
        return
    n = int(line)
    # lists per residue 0..4 storing tuples (name, cents)
    buckets = [[] for _ in range(5)]
    for _ in range(n):
        parts = input().split()
        if not parts:
            # if blank line, try again
            parts = input().split()
        name = parts[0]
        e = int(parts[1])
        s = int(parts[2])
        cents = e * 100 + s
        r = cents % 5
        buckets[r].append((name, cents))

    # initial groups: each item separately
    groups = []
    # We can reduce the total by 5 cents for each of these patterns:
    # (3,4), (3,3), (4,4,4). Choose the combination that yields the maximum
    # number of such patterns. Iterate p = number of (3,4) pairs and compute
    # how many (3,3) and (4,4,4) we can form from the leftovers.
    c3 = len(buckets[3])
    c4 = len(buckets[4])
    best = (-1, 0)  # (total_patterns, p)
    max_p = min(c3, c4)
    for p in range(max_p + 1):
        rem3 = c3 - p
        rem4 = c4 - p
        q = rem3 // 2  # number of (3,3)
        r = rem4 // 3  # number of (4,4,4)
        total = p + q + r
        if total > best[0]:
            best = (total, p)

    _, chosen_p = best
    # make chosen_p pairs of (3,4)
    for _ in range(chosen_p):
        a = buckets[3].pop()
        b = buckets[4].pop()
        groups.append([a, b])

    # now form (3,3) pairs from remaining 3s
    pairs_33 = len(buckets[3]) // 2
    for _ in range(pairs_33):
        a = buckets[3].pop()
        b = buckets[3].pop()
        groups.append([a, b])

    # and form (4,4,4) triples from remaining 4s
    triples_444 = len(buckets[4]) // 3
    for _ in range(triples_444):
        a = buckets[4].pop()
        b = buckets[4].pop()
        c = buckets[4].pop()
        groups.append([a, b, c])

    # add all leftover single items as individual groups
    for r in range(5):
        while buckets[r]:
            groups.append([buckets[r].pop()])

    # compute final total by rounding each group's total cents to nearest 5
    total_cents = 0
    out_groups = []
    for g in groups:
        names = [it[0] for it in g]
        group_cents = sum(it[1] for it in g)
        total_cents += round_to_5(group_cents)
        out_groups.append(names)

    euros = total_cents // 100
    cents = total_cents % 100

    # output
    out_lines = [f"{euros} {cents}"]
    for grp in out_groups:
        out_lines.append(" ".join(grp))

    sys.stdout.write("\n".join(out_lines))


if __name__ == "__main__":
    main()
