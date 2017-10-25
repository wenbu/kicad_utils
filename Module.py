'''
Classes and functions related to kicad_pcb module nodes.
'''
from KicadPcbNode import KicadPcbNode
from KicadPcbNode import find_nodes
from Transformable import Transformable
from numpy import array
from Transform2d import get_rotation_matrix, get_translation_matrix

def find_modules(nodes):
    ''' Get a list of Modules from a list of KicadPcbNodes. '''
    return find_nodes(nodes, Module)

class Module(Transformable):
    '''
    A kicad_pcb module. This is any KicadPcbNode named 'module', and
    represents a component on the PCB.
    '''
    node_type_name = 'module'

    def __init__(self, node):
        # pylint: disable=invalid-name
        self._node = node
        self._get_name()
        self.x, self.y, self.r = _get_position_and_rotation(node)
        self._get_pads()

    def _get_name(self):
        # look for node with name 'fp_text' whose first child is 'reference'
        # use the second child of this node as our name
        for child in self._node.get_children_with_name('fp_text'):
            fp_text_children = child.children
            if fp_text_children[0] == 'reference':
                self.name = fp_text_children[1]
                break
            else:
                continue

        if not self.name:
            raise Exception("Couldn't find a name!")

    def _get_pads(self):
        self._pads = self._node.get_children_with_name('pad')

    # Call this after changing self.x or self.y to update the underlying
    # KicadPcbNode.
    def _update_position(self):
        _get_at_node(self._node).children[:2] = [self.x, self.y]

    # Call this after changing self.r to update the underlying KicadPcbNode.
    def _update_rotation(self):
        _, _, old_rotation = _get_position_and_rotation(self._node)
        dr = self.r - old_rotation

        _get_at_node(self._node).children = [self.x, self.y, self.r]
        for child in self._node.children:
            child_at_node = _get_at_node(child)
            if child_at_node is not None:
                if child.name == 'model':
                    continue
                cx, cy, cr = _get_position_and_rotation(child)
                child_at_node.children = [cx, cy, cr + dr]

    def transform(self, t=(0, 0), r=0, rp=(0, 0)):
        T = get_translation_matrix(t=t)
        R = get_rotation_matrix(r=r, rp=rp)
        transform = T.dot(R)

        position = array([self.x, self.y, 1])
        self.x, self.y, _ = transform.dot(position).round(5)
        self._update_position()

        self.r += r
        self._update_rotation()



    def __str__(self):
        return "Module[%s, (%f, %f), %d]" % (self.name, self.x, self.y, self.r)

# Looks for a child of the specified node named 'at' and extracts position
# and rotation information from it.
def _get_position_and_rotation(node):
    at_node = _get_at_node(node)
    at_children = at_node.children

    # pylint: disable=invalid-name
    x, y = [float(x) for x in at_children[:2]]
    r = int(at_children[2]) if len(at_children) == 3 else 0
    return (x, y, r)

def _get_at_node(node):
    if not isinstance(node, KicadPcbNode):
        return None
    at_nodes = node.get_children_with_name('at')

    # pylint: disable=len-as-condition
    if len(at_nodes) == 0:
        return None
    elif len(at_nodes) == 1:
        return at_nodes[0]
    else:
        assert len(at_nodes) <= 1, "Unexpected number of child nodes" + \
                                   " with name 'at': %d" % len(at_nodes)
