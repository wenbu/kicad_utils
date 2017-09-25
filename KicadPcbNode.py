'''
Classes and functions related to .kicad_pcb files. Includes a KicadPcbNode
class and functions to parse and write .kicad_pcb files.
'''
import shlex

OUTPUT_INDENT_SIZE = 2

class KicadPcbNode(object):
    '''
    Represents a node in the kicad_pcb hierarchy.

    name is the node's name.
    children is a heterogeneous list composed of:
        - strings
        - ints
        - floats
        - KicadPcbNodes
    '''

    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        '''
        Add a child to this KicadPcbNode. This child can be numeric, a string,
        or a KicadPcbNode.
        '''
        self.children.append(_coerce(child))

    def get_children_with_name(self, name):
        '''
        Return a list of children of this KicadPcbNode that are themselves
        KicadPcbNodes and that have the specified name.
        '''
        return [c for c in self.children \
                if isinstance(c, KicadPcbNode) and c.name == name]

    def __str__(self):
        return '<%s>' % self.name

def parse_file(kicad_pcb_file_path):
    '''
    Parse a kicad_pcb file into a list of KicadPcbNodes.
    '''
    nodes = []
    nodes_in_progress = []
    with open(kicad_pcb_file_path, 'r') as kicad_pcb_file:
        for line in kicad_pcb_file:
            tokens = shlex.split(line, False, False)
            for token in tokens:
                nodes, nodes_in_progress = _parse_token(token, nodes, nodes_in_progress)

    # this should be an exception of some kind
    '''
    if len(self._nodes_in_progress) != 0:
        print 'Not all nodes were closed!'
        print 'Remaining %d nodes:' % len(self._nodes_in_progress)
        while len(self._nodes_in_progress) > 0:
            node = self._nodes_in_progress.pop()
            print node['name']
    '''
    return nodes

def _parse_token(token, nodes, nodes_in_progress):
    s_token, num_open, num_close = _handle_parens(token)
    # Assume that num_open can only ever be 0 or 1, and that num_close
    # is necessarily 0 if num_open is 1.
    if num_open == 1:
        _handle_new_node(s_token, nodes_in_progress)
        return (nodes, nodes_in_progress)

    _handle_arg(s_token, nodes_in_progress)

    if num_close > 0:
        _handle_closed_node(nodes, nodes_in_progress, num_close)

    return (nodes, nodes_in_progress)

def _handle_parens(token):
    '''
    Returns a tuple:
    (s_token, n_open, n_close), where
    s_token is the token stripped of leading and trailing parens,
    n_open is the number of leading parens, and
    n_close is the number of closing parens
    '''
    n_open = 0
    n_close = 0
    while token.startswith('('):
        token = token[1:]
        n_open += 1
    while token.endswith(')'):
        token = token[:-1]
        n_close += 1
    return (token, n_open, n_close)

def _handle_new_node(node_name, nodes_in_progress):
    new_node = KicadPcbNode(node_name)

    # If there is already a node in progress, then this new one must be
    # a child of the current node.
    if nodes_in_progress:
        current_node = nodes_in_progress[-1]
        current_node.add_child(new_node)

    nodes_in_progress.append(new_node)

def _handle_closed_node(nodes, nodes_in_progress, num_nodes_to_close):
    for _ in range(num_nodes_to_close):
        closed_node = nodes_in_progress.pop()
        if not nodes_in_progress:
            nodes.append(closed_node)

def _handle_arg(token, nodes_in_progress):
    if not token:
        return
    current_node = nodes_in_progress[-1]
    current_node.add_child(token)

def _coerce(child):
    if isinstance(child, KicadPcbNode):
        return child

    try:
        return int(child)
    except ValueError:
        # x is either a float or non-numeric
        try:
            return float(child)
        except ValueError:
            return child

def write_file(file_path, nodes):
    '''
    Write a KicadPcbNode tree to a file.
    '''
    with open(file_path, 'w') as output_file:
        for node in nodes:
            output_file.write(''.join(_write_node(node)) + '\n')

# returns a list of string components to be joined
def _write_node(node, indent_level=0):
    output = []

    indent = ' ' * (indent_level * OUTPUT_INDENT_SIZE)
    # An initial newline is only needed if we are not handling a
    # root-level node.
    initial_newline = indent_level != 0
    output.append('%s%s(%s' % ('\n' if initial_newline else '', \
                               indent if indent else '', \
                               node.name))

    def _is_last_child(i):
        return i == len(node.children) - 1

    for i, child in enumerate(node.children):
        if isinstance(child, KicadPcbNode):
            output.extend(_write_node(child, indent_level + 1))

            # If the last child is a node, put my closing paren on
            # a newline with appropriate indent.
            if _is_last_child(i):
                output.append('\n%s)' % indent)
        else:
            # If the last child is a string or number, put my closing
            # paren on the same line.
            output.append(' %s%s' % (str(child),\
                                     ')' if _is_last_child(i) else ''))

    return output
