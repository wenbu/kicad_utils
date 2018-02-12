'''
Classes and functions related to kicad_pcb via nodes.
'''
from KicadPcbNode import KicadPcbNode, find_nodes
from numpy import array
from Transform2d import Transformable, get_rotation_matrix, get_translation_matrix

def find_vias(nodes):
    ''' Get a list of Vias from a list of KicadPcbNodes. '''
    return find_nodes(nodes, Via)

class Via(Transformable):
    '''
    A kicad_pcb via. This is any KicadPcbNode named 'via'.
    '''
    node_type_name = 'via'

    def __init__(self, node):
        '''
        A via has the following attributes:
         - at: position (x, y)
         - size: size of via
         - drill: size of drill hole
         - layers: layers the via is on
         - net: net of via
        '''
        self._node = node

        self.position = array(_get_position(node) + [1])

    def transform(self, t=(0, 0), r=0, rp=(0, 0)):
        T = get_translation_matrix(t=t)
        R = get_rotation_matrix(r=r, rp=rp)
        transform = T.dot(R)

        self.position = transform.dot(self.position).round(5)
        self._update_node()

    def _update_node(self):
        _get_at_node(self._node).children[:2] = self.position[:2]

    def get_position(self):
        return tuple(self.position[:2])

    def __str__(self):
        return "Via(%f, %f)" % self.get_position()

    def __repr__(self):
        return self.__str__()

# Looks for a child of the specified node named 'at' and extracts position
# information from it.
def _get_position(node):
    at_node = _get_at_node(node)
    at_children = at_node.children

    # pylint: disable=invalid-name
    return [float(x) for x in at_children[:2]]

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