import sys

# Loeme kogu sisendi turvaliselt ja kiiresti
data = sys.stdin.read().strip().split()
if not data:
    sys.exit(0)

it = iter(data)
try:
    n = int(next(it))
except StopIteration:
    n = 0

participants = []  # list of (name, score)
for _ in range(n):
    try:
        name = next(it)
        score = int(next(it))
    except StopIteration:
        break
    participants.append((name, score))

# Sorteerime skoori järgi kahanevalt
participants.sort(key=lambda x: -x[1])

out_lines = []
i = 0
while i < len(participants):
    j = i
    # leiame grupi kõigi sama skooriga osalejate indeksivahemiku [i, j]
    while j + 1 < len(participants) and participants[j + 1][1] == participants[i][1]:
        j += 1

    start = i + 1
    end = j + 1
    if start == end:
        place_str = f"{start}."
    else:
        place_str = f"{start}.-{end}."

    for k in range(i, j + 1):
        out_lines.append(f"{place_str} {participants[k][0]}")

    i = j + 1

sys.stdout.write("\n".join(out_lines))
