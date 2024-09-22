from z3 import *

from enum import Enum

class Mode(Enum):
    STANDARD = 0
    EXPERT = 1

mode: Mode = Mode.EXPERT

sectors = 12 if mode == Mode.STANDARD else 18

comets = [Bool(f"comet_{i+1}") for i in range(sectors)]
gas_cloud = [Bool(f"gas_cloud_{i+1}") for i in range(sectors)]
dwarf = [Bool(f"dwarf_{i+1}") for i in range(sectors)]
asteroid = [Bool(f"asteroid_{i+1}") for i in range(sectors)]
empty = [Bool(f"empty_{i+1}") for i in range(sectors)]
planet_x = [Bool(f"planet_x_{i+1}") for i in range(sectors)]

celestials_corps = [comets, gas_cloud, dwarf, asteroid, empty, planet_x]
CELESTIALS_CORPS_NAME = ["Comets", "Gas Cloud", "Dwarf", "Asteroid", "Empty", "Planet X"]

s = Solver()

s.add(Sum(comets) == 2)
s.add(Sum(gas_cloud) == 2)

dwarf_num = 1 if mode == Mode.STANDARD else 4
s.add(Sum(dwarf) == dwarf_num)
s.add(Sum(asteroid) == 4)

empty_num = 2 if mode == Mode.STANDARD else 5
s.add(Sum(empty) == empty_num)
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

if mode == Mode.EXPERT:
    # s.add(comets[12] == False)
    s.add(comets[13] == False)
    s.add(comets[14] == False)
    s.add(comets[15] == False)
    # s.add(comets[16] == False)
    s.add(comets[17] == False)

# Gas clouds
# Each gas cloud is adjacent to at least one truly empty sector.
for i in range(1, sectors+1):
    s.add(If(gas_cloud[i%sectors] == True, Or(empty[(i-1)%sectors] == True, empty[(i+1)%sectors] == True), True))

# No dwarf planet is adjacent to Planet X.
for i in range(1, sectors+1):
    s.add(If(dwarf[i%sectors] == True, And(planet_x[(i-1)%sectors] == False, planet_x[(i+1)%sectors] == False), True))


# In Expert Mode, there are 4 dwarf planets total instead of 1. 
# They are in a band of exactly 6 sectors, with a dwarf planet at each end.
if mode == Mode.EXPERT:
    s.add(Or(
            [And(
                Sum([dwarf[i%sectors] for i in range(j, j+6)]) == 4,
                dwarf[(j)%sectors] == True,
                dwarf[(j+5)%sectors] == True
            ) for j in range(sectors)]))

# Each asteroid is adjacent to at least one other asteroid. 
# (This means that the asteroids are either in two separate pairs or in one group of four.)
for i in range(1, sectors+1):
    s.add(If(asteroid[i%sectors] == True, Or(asteroid[(i-1)%sectors] == True, asteroid[(i+1)%sectors] == True), True))

# Planet X is not adjacent to a dwarf planet.
for i in range(1, sectors+1):
    s.add(If(planet_x[i%sectors] == True, And(dwarf[(i-1)%sectors] == False, dwarf[(i+1)%sectors] == False), True))

for i in range(sectors):
    s.add(Sum(comets[i], gas_cloud[i], dwarf[i], asteroid[i], empty[i], planet_x[i]) == 1)

# Game simulation
# for i in range(2, sectors+2):
#     s.add(Implies(gas_cloud[i%sectors] == True, Or(comets[(i-2)%sectors] == True, comets[(i-1)%sectors] == True, comets[(i+1)%sectors] == True, comets[(i+2)%sectors] == True)))
# 
# s.add(Sum(asteroid[1], asteroid[2], asteroid[3], asteroid[4], asteroid[5], asteroid[6]) == 1)
# 
# for i in range(1,  sectors+1):
#     s.add(Implies(dwarf[i%sectors] == True, Or(gas_cloud[(i-1)%sectors] == True, gas_cloud[(i+1)%sectors] == True)))
# 
# s.add(Sum(asteroid[4], asteroid[5], asteroid[6], asteroid[7]) == 0)

i = 0
percentages = [[0.0 for _ in celestials_corps] for _ in range(sectors)]
while s.check() == sat:
    i += 1

    print(i)

    m = s.model()

    block = []
    for var in m:
        block.append(var() != m[var])
    s.add(Or(block))

    for sector in range(sectors):
        for corp in range(len(celestials_corps)):
            percentages[sector][corp] += is_true(m[celestials_corps[corp][sector]])

print(f"Total models: {i}")

import math

for sector in range(sectors):
    for corp in range(len(celestials_corps)):
        percentages[sector][corp] /= i

def format_results(percentages):
    pp = [{CELESTIALS_CORPS_NAME[i]: f"{(p[i]*100):.2f}%" for i in range(len(celestials_corps))} for p in percentages]
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

for i in range(len(celestials_corps)):
    entropy = 0.0
    for p in percentages:
        if p[i] == 0.0:
            continue
        entropy -= p[i] * math.log2(p[i])

    print(f"Entropy for {CELESTIALS_CORPS_NAME[i]}: {entropy:.2f}")