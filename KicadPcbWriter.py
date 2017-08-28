class KicadPcbWriter:
    def __init__(self, indent_size=2):
        self.indent_size = indent_size

    def write(self, file_path, tags):
        with open(file_path, 'w') as f:
            for line in self.get_lines(tags):
                f.write(line + '\n')

    def get_lines(self, tags):
        lines = []

        # list of tuples: tags, indent levels, number of tags to close
        tags_to_process = [(tag, 0, 0) for tag in tags]
        while len(tags_to_process) != 0:
            current_tag, indent_level, num_closures = tags_to_process.pop()

            current_line = []
            # Subtract one since the join operation at the end of the while
            # loop adds an extra space
            starting_indent = ' ' * (indent_level * self.indent_size - 1)
            if starting_indent:
                current_line.append(starting_indent)

            current_line.append('(%s' % current_tag['name'])
            for arg in current_tag['args']:
                current_line.append(str(arg))

            children = current_tag['children']

            # If no children, we can close ourselves and output the closing
            # parens from ancestors now.
            # Otherwise, push these onto the last child.
            can_close_now = (len(children) == 0)

            final_line = ' '.join(current_line)
            if can_close_now:
                final_line += ')'
            lines.append(final_line)

            if can_close_now:
                for i in range(num_closures):
                    indent_level -= 1
                    indent = ' ' * (indent_level * self.indent_size)
                    lines.append('%s)' % indent)

            # reverse children since we are adding them to a stack but still
            # want to visit them in the same order
            # could've just made it a queue but oh well
            for i, child in enumerate(children[::-1]):
                # last child is the one with index 0 due to reverse
                is_last_child = (i == 0)
                num_closures_for_child = 0
                if is_last_child and not can_close_now:
                    num_closures_for_child = num_closures + 1
                tags_to_process.append((child, \
                                        indent_level + 1, \
                                        num_closures_for_child))

        return lines