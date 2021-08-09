import textwrap

class NodePrettier(object):
    def __init__(self, parent, **childs):
        self.parent = parent
        self.childs = childs
    def __repr__(self):
        return build_tree(self)

def build_tree(node: NodePrettier):
    string = f"[:{node.parent}:]"
    items = tuple(node.childs.items())
    for cname, cvalue in items:
        head = f"[{cname}]"
        string += f"\n    "+head
        string += "\n"+textwrap.indent(
            cvalue.__repr__(),
            prefix="    "*2
        )
        string += "\n    [end]"
    return string+"\n[:end:]"