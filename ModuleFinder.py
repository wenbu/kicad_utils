from Module import Module

# This class makes some assumptions about the structure of
# the node hierarchy -- namely, that all module nodes are
# direct descendants of the kicad_pcb node, and that the
# kicad_pcb node is the only node at the root level.
class ModuleFinder:
	def __init__(self):
		pass

	def find_modules(self, nodes):
		kicad_pcb_node = nodes[0]
		if kicad_pcb_node.name != 'kicad_pcb':
			raise Exception("Root node name is not kicad_pcb but is %s!" %
				            kicad_pcb_node.name)

		return [Module(c) \
		        for c \
		        in kicad_pcb_node.get_children_with_name('module')]