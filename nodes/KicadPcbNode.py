'''
Classes and functions related to .kicad_pcb files. Includes a KicadPcbNode
class and functions to parse and write .kicad_pcb files.
'''
import shlex
from nodes.Transform2d import Transformable
from numbers import Number

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

    def add_named_child(self, name, values):
        '''
        Add a named child to this KicadPcbNode. This child becomes a KicadPcbNode itself
        with the specified name, and whose children are the specified values.
        '''
        named_child = KicadPcbNode(name)
        if hasattr(values, '__len__') and not isinstance(values, str):
            named_child.children = list(values)
        else:
            named_child.children = [values]
        self.children.append(named_child)

    def get_children_with_name(self, name):
        '''
        Return a list of children of this KicadPcbNode that are themselves
        KicadPcbNodes and that have the specified name.
        '''
        return [c for c in self.children \
                if isinstance(c, KicadPcbNode) and c.name == name]

    def get_child_with_name(self, name):
        '''
        Return the KicadPcbNode child of this KicadPcbNode with the specified name.
        This child must be the only child with the specified name; an exception
        will be raised otherwise.
        '''
        children_with_name = self.get_children_with_name(name)
        if len(children_with_name) != 1:
            raise Exception('Node %s has %d children with name %s.' %
                            (self.name, len(children_with_name), name))

        return children_with_name[0]

    def __getitem__(self, key):
        nodes_with_name = self.get_children_with_name(key)
        if len(nodes_with_name) == 1:
            children = nodes_with_name[0].children
            if len(children) == 1:
                return children[0]
            else:
                return children
        else:
            raise NotImplementedError(('There are %d children with the name %s.' +
                                       ' Not supported for now.') % (len(nodes_with_name), key))

    def __setitem__(self, key, value):
        existing_value = self.get_children_with_name(key)
        if len(existing_value) == 1:
            # child with unique name
            children = existing_value[0].children
            if not isinstance(value, str) and not hasattr(value, '__len__'):
                if len(children) == 1:
                    # Do a type check to ensure we aren't setting a string to
                    # a number or vice-versa.
                    existing_value_is_numeric = isinstance(children[0], Number)
                    new_value_is_numeric = isinstance(value, Number)
                    if existing_value_is_numeric == new_value_is_numeric:
                        children[0] = value
                    else:
                        raise Exception('Types don\'t match. Existing value: %s, new value: %s',
                                        str(children[0]), str(value))
                else:
                    raise Exception('Existing value has length %d.', len(existing_value))
            else:
                if len(children) == len(value):
                    types_match = True
                    for existing_child, new_child in zip(children, value):
                        existing_child_is_numeric = isinstance(existing_child, Number)
                        new_child_is_numeric = isinstance(new_child, Number)
                        if existing_child_is_numeric != new_child_is_numeric:
                            types_match = False
                            break
                    if types_match:
                        existing_value[0].children = list(value)
                    else:
                        raise Exception('Types don\'t match. Existing value: %s, new value: %s',
                                        str(children), str(value))
                else:
                    raise Exception('Lengths don\'t match. Existing length: %d, new length: %d',
                                    len(children), len(value))
        else:
            # TODO: what to do if there are multiple children with the same name?
            # e.g. fp_text, fp_line, pad
            raise NotImplementedError(('There are multiple children with the name %s.' +
                                       ' Not supported for now.') % key)

    def __str__(self):
        return '<%s> %s' % (self.name, [c.__str__() for c in self.children])

def find_nodes(nodes, node_class):
    '''
    Get a list of node_class from a list of KicadPcbNodes.
    node_class is assumed to have a class variable named 'node_type_name'
    that contains the node name to filter for.
    '''
    kicad_pcb_node = nodes[0]
    if kicad_pcb_node.name != 'kicad_pcb':
        raise Exception('Root node name is not kicad_pcb but is %s!' %
                        kicad_pcb_node.name)

    return [node_class(c) \
            for c \
            in kicad_pcb_node.get_children_with_name(node_class.node_type_name)]

'''
################################################
#
# Parser related functions
#
################################################
'''
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
    elif hasattr(child, '_node'):
        return child._node

    try:
        return int(child)
    except ValueError:
        # x is either a float or non-numeric
        try:
            return float(child)
        except ValueError:
            return child

'''
################################################
#
# File writing related functions
#
################################################
'''
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
