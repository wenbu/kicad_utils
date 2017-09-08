from KicadPcbNode import KicadPcbNode

class KicadPcbWriter(object):
    def __init__(self, indent_size=2):
        self.indent_size = indent_size

    def write(self, file_path, nodes):
        with open(file_path, 'w') as f:
            for node in nodes:
                f.write(''.join(self._handle_node(node)) + '\n')

    # returns a list of string components to be joined
    def _handle_node(self, node, indent_level=0):
        output = []

        indent = ' ' * (indent_level * self.indent_size)
        # An initial newline is only needed if we are not handling a
        # root-level node.
        initial_newline = indent_level != 0
        output.append('%s%s(%s' % ('\n' if initial_newline else '', \
                                   indent if indent else '', \
                                   node.name))

        def is_last_child(i):
            return i == len(node.children) - 1

        for i, child in enumerate(node.children):
            if isinstance(child, KicadPcbNode):
                output.extend(self._handle_node(child, indent_level + 1))

                # If the last child is a node, put my closing paren on
                # a newline with appropriate indent.
                if is_last_child(i):
                    output.append('\n%s)' % indent)
            else:
                # If the last child is a string or number, put my closing
                # paren on the same line.
                output.append(' %s%s' % (str(child),\
                                         ')' if is_last_child(i) else ''))

        return output
