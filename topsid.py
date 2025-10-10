# loeme sisendi esimese rea
number_cups, number_swaps, cup_with_ball = [int(v) for v in input().split()]

# loeme M vahetust
for i in range(number_swaps):
    # loeme vahetuse i andmed
    a, b = [int(v) for v in input().split()]
    if a == cup_with_ball:
        cup_with_ball = b
    elif b == cup_with_ball:
        cup_with_ball = a

# väljastame palli lõppasukoha
print(cup_with_ball)
