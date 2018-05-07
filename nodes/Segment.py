'''
Classes and functions related to kicad_pcb segment nodes.
'''
import math
from nodes.KicadPcbNode import find_nodes, KicadPcbNode
from numpy import array
from nodes.Transform2d import Transformable, get_rotation_matrix, get_translation_matrix

def find_segments(nodes):
    ''' Get a list of Segments from a list of KicadPcbNodes. '''
    return find_nodes(nodes, Segment)

class Segment(Transformable):
    '''
    A kicad_pcb segment. This is any KicadPcbNode named 'segment'.
    '''
    node_type_name = 'segment'

    def __init__(self, node):
        '''
        A segment has the following attributes:
         - start: start point
         - end: end point
         - width: width of segment
         - layer: layer of segment
         - net: net of segment
        '''
        self._node = node

        self.start = array(node['start'][0:2] + [1])
        self.end = array(node['end'][0:2] + [1])
        self.width = node['width']
        self.layer = node['layer']
        self.net = node['net']

    @classmethod
    def new_segment(cls, start=(0.0, 0.0), end=(0.0, 0.0), width=0.254, layer='', net=0):
        '''
        Create a new segment.
        '''
        node = KicadPcbNode('segment')
        node.add_named_child('start', start)
        node.add_named_child('end', end)
        node.add_named_child('width', width)
        node.add_named_child('layer', layer)
        node.add_named_child('net', net)
        return cls(node)

    def transform(self, t=(0, 0), r=0, rp=(0, 0)):
        T = get_translation_matrix(t=t)
        R = get_rotation_matrix(r=r, rp=rp)
        transform = T.dot(R)

        self.start = transform.dot(self.start).round(5)
        self.end = transform.dot(self.end).round(5)
        self._update_node()

    def _update_node(self):
        start_node = self._node.get_child_with_name('start')
        start_node.children[:2] = self.start[:2]

        end_node = self._node.get_child_with_name('end')
        end_node.children[:2] = self.end[:2]

    def get_start(self):
        '''Return the start position of this segment.'''
        return tuple(self.start[:2])

    def get_end(self):
        '''Return the end position of this segment.'''
        return tuple(self.end[:2])

    def get_other_end(self, position):
        '''If position is one end of this segment, return the
        position of the other end. If not, raise.'''
        if _distance(position, self.start[:2]) <= EPSILON:
            return self.get_end()
        elif _distance(position, self.end[:2]) <= EPSILON:
            return self.get_start()
        else:
            raise Exception("Position (%f, %f) is not an endpoint" % position)

    def __str__(self):
        return "Segment(%s: %s, %s)" % (self.layer, self.get_start(), self.get_end())

    def __repr__(self):
        return self.__str__()

EPSILON = 0.001
def _distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
