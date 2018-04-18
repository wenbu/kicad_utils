'''
Rotate components on Gaia PCB.
'''
from nodes.KicadPcbNode import parse_file, write_file
from nodes.Module import find_modules, Module
from nodes.Segment import find_segments
from nodes.Via import find_vias
import re
from quadtree.quadtree import Quadtree
from nodes.Transform2d import transform

# pylint: disable=all

GAIA_PATH = '../keyboard/gaia/gaia.kicad_pcb'
GAIA_OUTPUT = '../keyboard/gaia/gaia2.kicad_pcb'

nodes = parse_file(GAIA_PATH)
modules = find_modules(nodes)
segments = find_segments(nodes)
vias = find_vias(nodes)

def get_modules(*module_names):
    return [x for x in modules if x.name in module_names]

quadtree = Quadtree()
for module in modules:
    quadtree.insert(module)
for segment in segments:
    quadtree.insert(segment)
for via in vias:
    quadtree.insert(via)

# rotate thumb keys
left_thumbs = get_modules('S5:5', 'S5:6')
right_thumbs = get_modules('S5:7', 'S5:8')

# get thumb pivots
for module in modules:
    if module.name == 'S4:5':
        left_thumb_pivot_base = module.get_position()
    elif module.name == 'S4:8':
        right_thumb_pivot_base = module.get_position()
    else:
        continue

left_thumb_pivot = (left_thumb_pivot_base[0] + 9.525,
                    left_thumb_pivot_base[1] + 9.525)
right_thumb_pivot = (right_thumb_pivot_base[0] - 9.525,
                     right_thumb_pivot_base[1] + 9.525)

left_thumbs = quadtree.get_connected(left_thumbs)
right_thumbs = quadtree.get_connected(right_thumbs)

for left_thumb_node in left_thumbs:
    left_thumb_node.transform(r=-30, rp=left_thumb_pivot)
    quadtree.update(left_thumb_node)

for right_thumb_node in right_thumbs:
    right_thumb_node.transform(r=30, rp=right_thumb_pivot)
    quadtree.update(right_thumb_node)

left_side = []
right_side = []
key_pattern = re.compile('[DS]([0-9]+):([0-9]+)')
for module in modules:
    match = key_pattern.match(module.name)
    if match:
        second_digit = int(match.group(2))
        if second_digit <= 6:
            left_side.append(module)
        else:
            right_side.append(module)
left_side.extend(get_modules('SW1', 'Y1', 'C4', 'C5'))
right_side.extend(get_modules('C6', 'C7'))

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

left_side = quadtree.get_connected(left_side)
right_side = quadtree.get_connected(right_side)

for left_side_node in left_side:
    left_side_node.transform(t=(dx_6, dy))
    quadtree.update(left_side_node)

for right_side_node in right_side:
    right_side_node.transform(t=(dx_7, dy))
    quadtree.update(right_side_node)


# tilt sides up 10 degrees

left_pivot = (s1_6.x, s1_6.y)
for left_side_node in left_side:
    left_side_node.transform(r=-10, rp=left_pivot)

right_pivot = (s1_7.x, s1_7.y)
for right_side_node in right_side:
    right_side_node.transform(r=10, rp=right_pivot)

write_file(GAIA_OUTPUT, nodes)
