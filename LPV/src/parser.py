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

from LPV.src.error import ErrorType, LPV_Exception
from LPV.src.token import Token, TokenTree, TokenType
from typing import Callable, Iterable, Union
import traceback

class LPV_Parser:
    initiliaze = False
    def __init__(self):
        if not "start" in self.__dict__:
            raise TypeError("no self.start found")
        if not isinstance(self.start, Iterable):
            raise TypeError(
                "self.start must be iterable"
            )
        if len(self.start) < 2:
            raise TypeError(
                "self.start must have two element: function/function_name and arguments"
            )
        self.method, self.args = self.get_method(self.start[0]), self.start[1]
        self.initiliaze = True
        
    def get_method(self, func: Union[str, Callable]) -> Callable:
        if isinstance(func, str):
            if func.startswith("parse_"):
                name = func
            else:
                name = "parse_"+func
            m = getattr(self, name)
            if not isinstance(m, Callable):
                raise TypeError(f"{name} must be callable, not {type(m).__name__}")
            return m
        if not func.__name__.startswith("parse_"):
            raise TypeError(f"{func.__name__} name must start with parse_")
        return func
    
    def init(self, token_tree: TokenTree):
        self.tree, self.source = token_tree, token_tree.source
        self.token = None
        self.line, self.col = -1, -1
        self.next_token()
    
    def get_lc(self):
        return self.line, self.col
    
    def throw_error(self, error, msg, pointer_width:int=1, **kwargs):
        raise LPV_Exception(
            error=error, msg=msg,
            line=self.line, col=self.col,
            source=self.source, pointer_width=pointer_width,
            when="Parser", **kwargs
        )
    
    def next_token(self):
        old_t = self.token
        self.token = self.tree.next_token()
        self.line, self.col = self.tree.line, self.tree.col
        return old_t
    
    def is_eof(self):
        return self.token is None
    
    def eat(self, type_: Union[TokenType, Iterable]=None):
        if type_ is None or self.check_type(type_):
            return self.next_token()
        msg = "Unexpected "+("EOF" if self.is_eof() else f"'{self.token.value}'")
        self.throw_error(
            ErrorType.SYNTAX, msg+", expected "+(
                type_.name if isinstance(type_, TokenType) else " or ".join(type_)
            ),
        )
    
    def peek(self, step:int=1):
        return self.tree.peek(step)
        
    def check_type(self, type_: Union[TokenType, Iterable[TokenType]], token=False):
        if not isinstance(type_, (TokenType, Iterable)):
            raise TypeError("type_ must be TokenType or Iterable")
        if isinstance(type_, TokenType):
            if token is not False:
                return token == type_
            return self.token == type_
        if token is not False:
            for t in type_:
                if self.check_type(t, token=token):
                    return True
            return False
        for t in type_:
            if self.check_type(t):
                return True
        return False
    
    def eats(self, *types) -> list[Token]:
        tkns = []
        for t in types:
            tkns.append(self.eat(t))
        return tkns
    
    def match(self, *types):
        for i, t in enumerate(types):
            if not self.check_type(t, self.peek(i)):
                return False
        return True
    
    def parse(self, tree: TokenTree, crash_handler:Callable=print):
        if self.initiliaze is False:
            raise TypeError(
                f"{type(self).__name__} is not fully initiliaze. Forgot super().__init__() in the __init__?"
            )
        self.init(tree)
        try:
            r = self.method(*self.args)
        except LPV_Exception as e:
            raise e
        except Exception as e:
            if crash_handler is print:
                crash_handler(traceback.format_exc())
            else:
                crash_handler(e)
            self.throw_error(
                ErrorType.CRASH,
                "Uh oh. Looks like the parser got an Python Error."
            )
        else:
            return r