'''
Rotate components on Gaia PCB.
'''
from KicadPcbNode import parse_file, write_file
from Module import find_modules
from Segment import find_segments
import re

# pylint: disable=all

GAIA_PATH = '../../../keyboard/gaia/gaia.kicad_pcb'

nodes = parse_file(GAIA_PATH)
modules = find_modules(nodes)
segments = find_segments(nodes)

# rotate thumb keys
# find 5:5, 5:6 (L) and 5:7, 5:8 (R)
left_thumbs = []
right_thumbs = []
for module in modules:
    if module.name == 'S5:5' or module.name == 'S5:6':
        left_thumbs.append(module)
    elif module.name == 'S5:7' or module.name == 'S5:8':
        right_thumbs.append(module)
    else:
        continue

left_thumb_pivot = (209.55, 123.825)
right_thumb_pivot = (304.8, 123.825)

for left_thumb_module in left_thumbs:
    left_thumb_module.transform(r=-30, rp=left_thumb_pivot)

for right_thumb_module in right_thumbs:
    right_thumb_module.transform(r=30, rp=right_thumb_pivot)

# move right side keys to correct position
left_side = []
right_side = []
key_pattern = re.compile('S([0-9]+):([0-9]+)')
for module in modules:
    match = key_pattern.match(module.name)
    if match:
        second_digit = int(match.group(2))
        if second_digit <= 6:
            left_side.append(module)
        else:
            right_side.append(module)

# move right side such that S1:7 is 24.8063mm to the right of S1:6
# center around IC3
ic3 = [x for x in modules if x.name == 'IC3'][0]
s1_6 = [x for x in modules if x.name == 'S1:6'][0]
s1_7 = [x for x in modules if x.name == 'S1:7'][0]
target_x_6 = ic3.x - (24.8063/2)
target_x_7 = ic3.x + (24.8063/2)
target_y = s1_6.y
dx_6 = target_x_6 - s1_6.x
dx_7 = target_x_7 - s1_7.x
dy = target_y - s1_7.y

for left_side_key in left_side:
    left_side_key.transform(t=(dx_6, dy))

for right_side_key in right_side:
    right_side_key.transform(t=(dx_7, dy))


# tilt sides up 10 degrees

left_pivot = (s1_6.x, s1_6.y)
for left_side_key in left_side:
    left_side_key.transform(r=-10, rp=left_pivot)

right_pivot = (s1_7.x, s1_7.y)
for right_side_key in right_side:
    right_side_key.transform(r=10, rp=right_pivot)

write_file(GAIA_PATH, nodes)
