from KicadPcbParser import KicadPcbParser
from KicadPcbWriter import KicadPcbWriter
from ModuleFinder import ModuleFinder
from Transform2d import rotate_about_pivot

parser = KicadPcbParser()
nodes = parser.parse('../keyboard/gaia/gaia.kicad_pcb')

finder = ModuleFinder()
modules = finder.find_modules(nodes)

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
	x, y, r = left_thumb_module.x, left_thumb_module.y, left_thumb_module.r
	nx, ny = rotate_about_pivot(x, y, 30, *left_thumb_pivot)
	left_thumb_module.set_position(nx, ny)
	left_thumb_module.set_rotation(r + 30)

for right_thumb_module in right_thumbs:
	x, y, r = right_thumb_module.x, right_thumb_module.y, right_thumb_module.r
	nx, ny = rotate_about_pivot(x, y, -30, *right_thumb_pivot)
	right_thumb_module.set_position(nx, ny)
	right_thumb_module.set_rotation(r - 30)

writer = KicadPcbWriter()
writer.write('../keyboard/gaia/gaia.kicad_pcb', nodes)