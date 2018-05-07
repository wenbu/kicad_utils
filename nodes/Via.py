'''
Classes and functions related to kicad_pcb via nodes.
'''
from nodes.KicadPcbNode import KicadPcbNode, find_nodes
from numpy import array
from nodes.Transform2d import Transformable, get_rotation_matrix, get_translation_matrix

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

        self.position = array(node['at'][0:2] + [1])
        self.size = node['size']
        self.drill = node['drill']
        self.layers = node['layers']
        self.net = node['net']

    @classmethod
    def new_via(cls, position=(0.0, 0.0), size=0.889, drill=0.635, layers=('F.Cu', 'B.Cu'), net=0):
        '''
        Create a new via.
        '''
        node = KicadPcbNode('via')
        node.add_named_child('at', position)
        node.add_named_child('size', size)
        node.add_named_child('drill', drill)
        node.add_named_child('layers', layers)
        node.add_named_child('net', net)
        return cls(node)

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
