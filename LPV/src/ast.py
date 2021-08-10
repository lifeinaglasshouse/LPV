# MIT License

# Copyright (c) 2021 xp

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from typing import Callable
from LPV.src.error import ErrorType, LPV_Exception
from LPV.tools.prettier import NodePrettier
import traceback

class Node:
    
    def __init__(self, line:int, col:int=None):
        self.line, self.col = line, col
        self.node_name = type(self).__name__
    def __repr__(self) -> str:
        d = self.__dict__.copy()
        d.pop("line")
        d.pop("col")
        d.pop("node_name")
        return NodePrettier(
            self.node_name,
            **d
        ).__repr__()

class NodeVisitor:
    last_node = None
    def visit(self, node: Node):
        self.last_node = node
        return getattr(self, "visit_"+node.node_name, self.visit_error)(node)
    
    def visit_error(self, node: Node):
        raise NameError(f"no visit_{node.node_name} found")
    
    def visits(self, *nodes: Node):
        return (self.visit(node) for node in nodes)
    
    def throw_error(self, error, msg, node: Node, pointer_width:int=1, **kwargs):
        raise LPV_Exception(
            error=error, msg=msg,
            line=node.line, col=node.col,
            source=self.source,
            pointer_width=pointer_width,
            when="Runtime",
            **kwargs
        )
    
    def run(self, node_tree: Node, source: str, crash_handler:Callable=print):
        self.tree = node_tree
        self.source = source
        try:
            r = self.visit(self.tree)
        except LPV_Exception as e:
            raise e
        except Exception as e:
            if crash_handler is print:
                crash_handler(traceback.format_exc())
            else:
                crash_handler(e)
            self.throw_error(
                ErrorType.CRASH,
                f"Uh oh. Looks like the interpreter got an Python Error.",
                self.last_node
            )
        else:
            return r