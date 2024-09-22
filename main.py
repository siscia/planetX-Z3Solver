
from z3 import *

size = 12

comets = [Bool(f"comet_{i+1}") for i in range(size)]
gas_cloud = [Bool(f"gas_cloud_{i+1}") for i in range(size)]
dwarf = [Bool(f"dwarf_{i+1}") for i in range(size)]
asteroid = [Bool(f"asteroid_{i+1}") for i in range(size)]
empty = [Bool(f"empty_{i+1}") for i in range(size)]
planet_x = [Bool(f"planet_x_{i+1}") for i in range(size)]

celetials_corps = [comets, gas_cloud, dwarf, asteroid, empty, planet_x]
CELETIALS_CORPS_NAME = ["Comets", "Gas Cloud", "Dwarf", "Asteroid", "Empty", "Planet X"]

s = Solver()

s.add(Sum(comets) == 2)
s.add(Sum(gas_cloud) == 2)
s.add(Sum(dwarf) == 1)
s.add(Sum(asteroid) == 4)
s.add(Sum(empty) == 2)
s.add(Sum(planet_x) == 1)

# Comets can be only in very specific sectors
# the sector that are not false.
s.add(comets[0] == False)
# s.add(comets[1] == False)
# s.add(comets[2] == False)
s.add(comets[3] == False)
# s.add(comets[4] == False)
s.add(comets[5] == False)
# s.add(comets[6] == False)
s.add(comets[7] == False)
s.add(comets[8] == False)
s.add(comets[9] == False)
# s.add(comets[10] == False)
s.add(comets[11] == False)

# Gas clouds
# Each gas cloud is adjacent to at least one truly empty sector.
for i in range(1, size+1):
    s.add(If(gas_cloud[i%size] == True, Or(empty[(i-1)%size] == True, empty[(i+1)%size] == True), True))

# No dwarf planet is adjacent to Planet X.
for i in range(1, size+1):
    s.add(If(dwarf[i%size] == True, And(planet_x[(i-1)%size] == False, planet_x[(i+1)%size] == False), True))

# Each asteroid is adjacent to at least one other asteroid. 
# (This means that the asteroids are either in two separate pairs or in one group of four.)
for i in range(1, size+1):
    s.add(If(asteroid[i%size] == True, Or(asteroid[(i-1)%size] == True, asteroid[(i+1)%size] == True), True))

# Planet X is not adjacent to a dwarf planet.
for i in range(1, size+1):
    s.add(If(planet_x[i%size] == True, And(dwarf[(i-1)%size] == False, dwarf[(i+1)%size] == False), True))

for i in range(size):
    s.add(Sum(comets[i], gas_cloud[i], dwarf[i], asteroid[i], empty[i], planet_x[i]) == 1)

# Game simulation
# for i in range(2, size+2):
#     s.add(Implies(gas_cloud[i%size] == True, Or(comets[(i-2)%size] == True, comets[(i-1)%size] == True, comets[(i+1)%size] == True, comets[(i+2)%size] == True)))
# 
# s.add(Sum(asteroid[1], asteroid[2], asteroid[3], asteroid[4], asteroid[5], asteroid[6]) == 1)
# 
# for i in range(1,  size+1):
#     s.add(Implies(dwarf[i%size] == True, Or(gas_cloud[(i-1)%size] == True, gas_cloud[(i+1)%size] == True)))

# s.add(Sum(asteroid[4], asteroid[5], asteroid[6], asteroid[7]) == 0)

i = 0
percentages = [[0.0 for _ in celetials_corps] for _ in range(size)]
while s.check() == sat:
    i += 1

    m = s.model()

    block = []
    for var in m:
        block.append(var() != m[var])
    s.add(Or(block))

    for sector in range(size):
        for corp in range(len(celetials_corps)):
            percentages[sector][corp] += is_true(m[celetials_corps[corp][sector]])

print(f"Total models: {i}")

import math

for sector in range(size):
    for corp in range(len(celetials_corps)):
        percentages[sector][corp] /= i

def format_results(percentages):
    pp = [{CELETIALS_CORPS_NAME[i]: f"{(p[i]*100):.2f}%" for i in range(len(celetials_corps))} for p in percentages]
    return {f"Sector {i+1:02d}": v for i, v in enumerate(pp)}

import pprint
pprint.pprint(format_results(percentages))

print()

for sector_n, p in enumerate(percentages):
    entropy = 0.0
    for i in p:
        if i == 0.0:
            continue
        entropy -= i * math.log2(i)

    print(f"Entropy for sector {sector_n+1}: {entropy:.2f}")

print()

for i in range(len(celetials_corps)):
    entropy = 0.0
    for p in percentages:
        if p[i] == 0.0:
            continue
        entropy -= p[i] * math.log2(p[i])

    print(f"Entropy for {CELETIALS_CORPS_NAME[i]}: {entropy:.2f}")