from KicadNode import KicadNode

class Module:
	def __init__(self, node):
		self.node = node
		self.init_from_node()

	def _init_from_node(self)
		# look for node with name 'fp_text' whose first child is 'reference'
		# use the second child of this node as our name
		for child in self.node.children:
			if child.name != 'fp_text':
				continue
			fp_text_children = child.children
			if fp_text_children[0] == 'reference':
				self.name = fp_text_children[1]
				break
			else:
				continue

		if not self.name:
			raise Exception("Couldn't find a name!")

	# TODO: get position (and rotation if present)