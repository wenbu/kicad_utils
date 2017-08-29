"""
Represents a node in the kicad_pcb hierarchy.

name is the node's name.
children is a heterogeneous list composed of:
    - strings
    - ints
    - floats
    - KicadNodes
"""
class KicadPcbNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(_coerce(child))

    def __str__(self):
        return '<%s>' % self.name

def _coerce(x):
    if isinstance(x, KicadPcbNode):
        return x

    try:
        i = int(x)
        return i
    except:
        # x is either a float or non-numeric
        try:
            f = float(x)
            return f
        except:
            return x