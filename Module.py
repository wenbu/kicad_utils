'''
Classes and functions related to kicad_pcb module nodes.
'''
from KicadPcbNode import KicadPcbNode

def find_modules(nodes):
    '''
    Get a list of modules in a list of KicadPcbNodes.
    '''
    kicad_pcb_node = nodes[0]
    if kicad_pcb_node.name != 'kicad_pcb':
        raise Exception("Root node name is not kicad_pcb but is %s!" %
                        kicad_pcb_node.name)

    return [Module(c) \
            for c \
            in kicad_pcb_node.get_children_with_name('module')]

class Module(object):
    '''
    A kicad_pcb module. This is any KicadPcbNode named 'module', and
    represents a component on the PCB.
    '''
    def __init__(self, node):
        # pylint: disable=invalid-name
        self.node = node
        self._get_name()
        self.x, self.y, self.r = _get_position_and_rotation(node)
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

    def _get_pads(self):
        self.pads = self.node.get_children_with_name('pad')


    # pylint: disable=invalid-name
    def set_position(self, x, y):
        '''
        Set the position of this module to (x, y).
        '''
        self.x, self.y = x, y
        _get_at_node(self.node).children = [x, y, self.r]

    def set_rotation(self, r):
        '''
        Set the rotation of this module to r degrees.
        '''
        self.r = r
        # KiCAD's rotation direction is clockwise
        _get_at_node(self.node).children = [self.x, self.y, -r]
        for child in self.node.children:
            child_at_node = _get_at_node(child)
            if child_at_node is not None:
                if child.name == 'model':
                    continue
                # pylint: disable=invalid-name
                cx, cy, _ = _get_position_and_rotation(child)
                child_at_node.children = [cx, cy, -r]

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
