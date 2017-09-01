from KicadPcbParser import KicadPcbParser
from KicadPcbWriter import KicadPcbWriter
from ModuleFinder import ModuleFinder

parser = KicadPcbParser()
nodes = parser.parse('../../../keyboard/gaia/gaia.kicad_pcb')

finder = ModuleFinder()
modules = finder.find_modules(nodes)

# find 5:5, 5:6 (L) and 5:7, 5:8 (R)
left_thumbs = []
right_thumbs = []
for module in modules:
    if module.name == 'S5:5' or module.name == 'S5:6':
        left_thumbs.append(module)
    elif module_name == 'S5:7' or module.name == 'S5:8':
        right_thumbs.append(module)
    else:
        continue

left_thumb_pivot = (209.55, 123.825)
right_thumb_pivot = (304.8, 123.825)

writer = KicadPcbWriter()
writer.write('../../../keyboard/gaia/gaia.kicad_pcb', nodes)