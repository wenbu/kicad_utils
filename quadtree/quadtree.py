'''
Quadtree
'''
import math
from nodes.Segment import Segment
from nodes.Via import Via
from nodes.Module import Module

MAX_NODE_SIZE = 5
EPSILON = 0.001

DEBUG = False

def _log(msg):
    if DEBUG:
        print msg

class Quadtree(object):
    def __init__(self):
        self.root = QuadtreeNode()
        self.contents = {}

    def insert(self, node):
        if isinstance(node, Segment):
            positions = [node.get_start(), node.get_end()]
        elif isinstance(node, Via):
            positions = [node.get_position()]
        elif isinstance(node, Module):
            positions = node.get_pad_positions()
        else:
            raise Exception("Cannot insert")

        for position in positions:
            self.root.insert(position, node)
        self.contents[node] = positions

    def update(self, node):
        '''Update node's position.'''
        for old_position in self.contents[node]:
            self.root.remove(old_position, node)

        del self.contents[node]
        self.insert(node)


    def lookup(self, position, epsilon=EPSILON):
        return self.root.lookup(position, epsilon)

    def get_connected(self, modules, desired_return_types=(Segment, Via)):
        positions = []
        for module in modules:
            pad_positions = [(pad_position, module) for pad_position in module.get_pad_positions()]
            if module.name == 'S0:4' or module.name == 'S0:5':
                print [p[0] for p in pad_positions]
            positions.extend(pad_positions)
        visited_positions = set()

        connected = set(modules)
        try:
            current_position, current_node = positions.pop()
            visited_positions.add(current_position)
        except IndexError:
            return connected

        while current_position is not None:
            connected_nodes = self.lookup(current_position)
            '''
            connected_nodes.remove(current_node)
            if self._contains_module(connected_nodes):
                print 'skipping -- current = %s' % connected_nodes
                current_position, current_node = self._get_next_position(positions, visited_positions)
                continue
                '''
            for connected_node in connected_nodes:
                if type(connected_node) in desired_return_types:
                    connected.add(connected_node)
                    if isinstance(connected_node, Segment):
                        positions.append((connected_node.get_other_end(current_position), connected_node))
                else:
                    continue

            current_position, current_node = self._get_next_position(positions, visited_positions)

        return connected

    @staticmethod
    def _contains_module(nodes):
        for node in nodes:
            if isinstance(node, Module):
                return True
        return False

    @staticmethod
    def _get_next_position(positions, visited_positions):
        try:
            next_position, next_node = positions.pop()
            while next_position in visited_positions:
                next_position, next_node = positions.pop()
            visited_positions.add(next_position)
            return (next_position, next_node)
        except IndexError:
            return (None, None)

'''
     ^
     |
 [0] | [1]
 ____|_____>
     |
 [2] | [3]
     |

'''
class QuadtreeNode(object):
    def __init__(self):
        self.leaves = []
        self.quadrants = []
        self.splitpoint = None

    def insert(self, position, node):
        if not self._is_split():
            if len(self.leaves) < MAX_NODE_SIZE:
                self.leaves.append(QuadtreeLeaf(position, node))
                return
            else:
                self._split()
        self._get_quadrant(position).insert(position, node)

    def remove(self, position, node):
        if not self._is_split():
            self.leaves = [leaf for leaf in self.leaves if leaf.node is not node]
        else:
            self._get_quadrant(position).remove(position, node)

    def lookup(self, position, epsilon=EPSILON):
        if self._is_split():
            '''
            dx = abs(self.splitpoint[0] - position[0])
            dy = abs(self.splitpoint[1] - position[1])
            if (dx > EPSILON/10 and dx <= EPSILON) or (dy > EPSILON/10 and dy <= EPSILON):
                ret = []
                for quadrant in self.quadrants:
                    qlookup = quadrant.lookup(position, epsilon)
                    print len(qlookup)
                    ret.extend(qlookup)
                return ret
            else:
                '''
            return self._get_quadrant(position).lookup(position, epsilon)
        else:
            return [qleaf.node for qleaf in self.leaves \
                    if _distance(qleaf.position, position) <= epsilon]
        # TODO this will miss the cases where the point is within epsilon distance
        # of this qnode's boundary

    def insert_leaf(self, qleaf):
        self.leaves.append(qleaf)

    def _split(self):
        # average positions of children -- this is the split point
        self.splitpoint = (_mean([leaf.position[0] for leaf in self.leaves]),
                           _mean([leaf.position[1] for leaf in self.leaves]))

        self.quadrants = [QuadtreeNode(), QuadtreeNode(), QuadtreeNode(), QuadtreeNode()]
        for leaf in self.leaves:
            self._get_quadrant(leaf.position).insert_leaf(leaf)
        self.leaves = []
    
    def _get_quadrant(self, point):
        X = self.splitpoint[0]
        Y = self.splitpoint[1]
        x = point[0]
        y = point[1]

        if x >= X:
            if y >= Y:
                return self.quadrants[1]
            else:
                return self.quadrants[3]
        else:
            if y >= Y:
                return self.quadrants[0]
            else:
                return self.quadrants[2]

    def _is_split(self):
        return self.splitpoint is not None

class QuadtreeLeaf(object):
    def __init__(self, position, node):
        self.position = position
        self.node = node

def _mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def _distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
