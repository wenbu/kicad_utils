import shlex
from KicadPcbNode import KicadPcbNode

'''
Parse the kicad_pcb file into a list of KicadNodes
'''
class KicadPcbParser(object):
    def __init__(self):
        self._nodes = []
        self._nodes_in_progress = []

    def parse(self, file_path):
        self._nodes = []
        with open(file_path, 'r') as f:
            for line in f:
                tokens = shlex.split(line, False, False)
                for token in tokens:
                    self._parse_token(token)

        # this should be an exception of some kind
        '''
        if len(self._nodes_in_progress) != 0:
            print 'Not all nodes were closed!'
            print 'Remaining %d nodes:' % len(self._nodes_in_progress)
            while len(self._nodes_in_progress) > 0:
                node = self._nodes_in_progress.pop()
                print node['name']
        '''
        return self._nodes

    def _parse_token(self, token):
        s_token, num_open, num_close = self._handle_parens(token)

        # Assume that num_open can only ever be 0 or 1, and that num_close
        # is necessarily 0 if num_open is 1.
        if num_open == 1:
            self._handle_new_node(s_token)
            return

        self._handle_arg(s_token)

        if num_close > 0:
            self._handle_closed_node(num_close)

    # Returns a tuple:
    # (s_token, n_open, n_close)
    # where s_token is the token stripped of leading and trailing parens,
    # n_open is the number of leading parens, and
    # n_close is the number of closing parens
    def _handle_parens(self, token):
        n_open = 0
        n_close = 0
        while token.startswith('('):
            token = token[1:]
            n_open += 1
        while token.endswith(')'):
            token = token[:-1]
            n_close += 1
        return (token, n_open, n_close)

    def _handle_new_node(self, node_name):
        new_node = KicadPcbNode(node_name)

        # If there is already a node in progress, then this new one must be
        # a child of the current node.
        if self._nodes_in_progress:
            current_node = self._nodes_in_progress[-1]
            current_node.add_child(new_node)

        self._nodes_in_progress.append(new_node)

    def _handle_closed_node(self, num_nodes_to_close=1):
        for i in range(num_nodes_to_close):
            closed_node = self._nodes_in_progress.pop()
            if not self._nodes_in_progress:
                self._nodes.append(closed_node)

    def _handle_arg(self, token):
        if not token:
            return
        current_node = self._nodes_in_progress[-1]
        current_node.add_child(token)