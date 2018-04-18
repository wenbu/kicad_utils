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

write_file(GAIA_OUTPUT, nodes)
