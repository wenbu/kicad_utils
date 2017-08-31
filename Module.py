class Module:
	def __init__(self, node):
		self.node = node
		self._get_name()
		self._get_position_and_rotation()
		self._get_pads()

	def _get_name(self):
		# look for node with name 'fp_text' whose first child is 'reference'
		# use the second child of this node as our name
		for child in self.node.get_children_with_name('fp_text'):
			fp_text_children = child.children
			if fp_text_children[0] == 'reference':
				self.name = fp_text_children[1]
				break
			else:
				continue

		if not self.name:
			raise Exception("Couldn't find a name!")

	# Looks for a child of the specified node named 'at' and extracts position
	# and rotation information from it.
	def _get_position_and_rotation(self, node):
		at_nodes = node.get_children_with_name('at')
		assert len(at_nodes) == 1, "Unexpected number of child nodes" + \
				                   "with name 'at': %d" % len(at_nodes)

		at_node = at_nodes[0]
		at_children = at_node.children

		x, y = [float(x) for x in at_children[:2]]
		r = int(at_children[2]) if len(at_children) == 3 else 0

	def _get_pads(self):
		self.pads = self.node.get_children_with_name('pad')


	def set_position(self, x, y):
		self.position = (x, y)
		self.at_node.children = [x, y, self.rotation]

	def set_rotation(self, r):
		self.rotation = r
		self.at_node.children = [self.position[0], self.position[1], r]

	def __str__(self):
		return "Module[%s, %s, %d]" % (self.name, str(self.position), self.rotation)
