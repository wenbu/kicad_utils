import shlex

'''
Parse the kicad_pcb file into a list of tags, where:

tag := { name:tag_name, args:[arg_list], children:[child_tag_list] }

args can be either numeric or strings.

TODO UGH: args and children list need to be combined into one, since some args
can come after children. (see hide attr, USB-MINI-B module)
'''
class KicadPcbParser:
    def __init__(self):
        self.tags = []
        self.tags_in_progress = []

    def parse(self, file_path):
        with open(file_path, 'r') as f:
            for line in f:
                #tokens = line.split()
                tokens = shlex.split(line, False, False)
                for token in tokens:
                    self.parse_token(token)

        # this should be an exception of some kind
        '''
        if len(self.tags_in_progress) != 0:
            print 'Not all tags were closed!'
            print 'Remaining %d tags:' % len(self.tags_in_progress)
            while len(self.tags_in_progress) > 0:
                tag = self.tags_in_progress.pop()
                print tag['name']
        '''
        return self.tags

    def parse_token(self, token):
        s_token, num_open, num_close = self.check_tag_changes(token)

        # Assume that num_open can only ever be 0 or 1, and that num_close
        # is necessarily 0 if num_open is 1.
        if num_open == 1:
            self.handle_new_tag(s_token)
            return

        self.handle_arg(s_token)

        if num_close > 0:
            self.handle_closed_tag(num_close)

    # Returns a tuple:
    # (s_token, n_open, n_close)
    # where s_token is the token stripped of leading and trailing parens,
    # n_open is the number of leading parens, and
    # n_close is the number of closing parens
    def check_tag_changes(self, token):
        n_open = 0
        n_close = 0
        while token.startswith('('):
            token = token[1:]
            n_open += 1
        while token.endswith(')'):
            token = token[:-1]
            n_close += 1
        return (token, n_open, n_close)

    def handle_new_tag(self, tag_name):
        #print '--New tag: %s' % tag_name
        new_tag = {'name':tag_name, 'args':[], 'children':[]}
        if len(self.tags_in_progress) > 0:
            current_tag = self.tags_in_progress[-1]
            current_tag['children'].append(new_tag)
        self.tags_in_progress.append(new_tag)

    def handle_closed_tag(self, num_tags_to_close=1):
        for i in range(num_tags_to_close):
            closed_tag = self.tags_in_progress.pop()
            if len(self.tags_in_progress) == 0:
                self.tags.append(closed_tag)

    def handle_arg(self, token):
        if len(token) == 0:
            return
        current_tag = self.tags_in_progress[-1]
        current_tag['args'].append(_coerce(token))
    
def _coerce(x):
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