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
from LPV.src.token import Token, TokenTree
from LPV.src.error import ErrorType, LPV_Exception
from typing import Callable, Union
import traceback

class LPV_Lexer:
    initiliazing = False
    def __init__(self, do_count_char:bool=False):
        self.can_count = do_count_char
        if do_count_char:
            self.count_char = 0
        if not "rules" in self.__dict__:
            raise TypeError("no self.rules found")
        r = []
        for k, v in (self.rules.items()) if isinstance(self.rules, dict) else (self.rules):
            is_callable = isinstance(v, Callable)
            if not is_callable and isinstance(v, str):
                r.append((k, getattr(self, ('lex_'+v) if not v.startswith("lex_") else v)))
            elif is_callable:
                if not v.__name__.startswith("lex_"):
                    raise TypeError(
                        f"self.rules rule function must start with 'lex_': {v.__name__}"
                    )
                r.append((k, v))
            else:
                raise TypeError(
                    f"{v} is not Callable or str"
                )
        if not r:
            raise TypeError(
                "self.rules can't be empty"
            )
        self.rules = tuple(r)
        self.name = type(self).__name__
        self.initiliazing = True
    
    def init(self, source: str):
        self.source, self.len_s = source, len(source)
        self.pos, self.char = -1, None
        self.chars = ""
        self.line, self.col = 0, -1
        self.next_char()
    
    def throw_error(self, error, msg, pointer_width:int=1, **kwargs):
        raise LPV_Exception(
            error=error, msg=msg,
            line=self.line, col=self.col,
            source=self.source, when="Lexer",
            pointer_width=pointer_width,
            **kwargs
        )
    
    def increase_count(self, num:int=1):
        if self.can_count is True:
            self.count_char += num
    def reset_count(self):
        if self.can_count is True:
            self.count_char = 0
    def get_count(self):
        if self.can_count is True:
            return (self.count_char,)
        return ()
    
    def next_char(self):
        self.pos += 1
        self.col += 1
        if self.pos >= self.len_s:
            self.char = None
        else:
            self.char = self.source[self.pos]
            if self.char == "\n":
                self.line += 1
                self.col = -1
    
    def peek(self, step=1):
        pos = self.pos+step
        if pos >= self.len_s:
            return None
        return self.source[pos]
    
    def enter(self, step=1):
        for _ in range(step):
            self.chars += self.char
            self.next_char()
    
    def skip(self, step=1):
        for _ in range(step):
            self.next_char()
    
    def clear(self):
        c = self.chars
        self.chars = ""
        return c
    
    def enter_clear(self, step=1):
        self.enter(step=step)
        return self.clear()
    
    def skip_clear(self, step=1):
        self.skip(step=step)
        return self.clear()
    
    def enter_while(self, expr: Callable):
        while not self.is_eof() and expr(self.char):
            self.enter()

    def skip_while(self, expr: Callable):
        while not self.is_eof() and expr(self.char):
            self.skip()    
    
    def slice(self, step:int, start:int=0):
        r = ""
        for i in range(step):
            c = self.peek(start+i)
            if c is not None:
                r += c
        return r
    
    def match_string(self, string: str, start:int=0, incase_sensitive:bool=False):
        slc = self.slice(len(string), start)
        r = (string == slc) if incase_sensitive is False else (string.lower() == slc.lower())
        if r is True:
            self.increase_count(len(string))
        return r
    
    def match_optional(self, *objs, **kwargs):
        for o in objs:
            if self.match(o, **kwargs):
                return True
        return False
    
    def match_optional(self, *objs, **kwargs):
        for o in objs:
            if self.match(o, **kwargs):
                return True
        return False

    def match_optional_incase(self, *objs, **kwargs):
        kwargs["incase_sensitive"] = True
        for o in objs:
            if self.match(o, **kwargs):
                return True
        return False

    def match_forward(self, *objs):
        for i, o in enumerate(objs):
            if not self.match(o, start=i):
                return False
        return True
    
    def match(self, obj: Union[tuple, list, set, str, Callable], **kwargs):
        if isinstance(obj, str):
            return self.match_string(obj, **kwargs)
        elif isinstance(obj, tuple):
            return self.match_forward(*obj)
        elif isinstance(obj, list):
            return self.match_optional(*obj, **kwargs)
        elif isinstance(obj, set):
            return self.match_optional_incase(*obj, **kwargs)
        elif isinstance(obj, Callable):
            arg = self.peek(kwargs["start"]) if "start" in kwargs else self.char
            if arg is None:
                return False
            r = True if obj(arg) else False
            if r is True:
                self.increase_count()
            return r
        else:
            raise TypeError(f"Only accept type tuple, list, str or Callable: {obj}")
    
    def is_eof(self):
        return self.char is None
    
    def put(self, string: str):
        self.chars += string
    
    def lex(self, source: str, ignore_un_update_pos:bool=False, crash_handler:Callable=print):
        if self.initiliazing is False:
            raise TypeError(
                f"{type(self).__name__} is not fully initiliaze. Forgot super().__init__() in the __init__?"
            )
        self.init(source)
        tree = []
        last_items = self.rules[-1]
        try:
            while not self.is_eof():
                lc = self.line, self.col
                for rule, func in self.rules:
                    self.reset_count()
                    if self.match(rule):
                        if ignore_un_update_pos is False:
                            p = self.pos
                            r = func(*self.get_count())
                            if self.pos == p:
                                raise TypeError(
                                    f"{func.__name__} must move to the next position atleast once"
                                    "(avoiding infinity loop)"
                                )
                        else:
                            r = func()
                        if r is None:
                            break
                        if not isinstance(r, Token):
                            raise TypeError("function must return Token object")
                        if None in (r.line, r.col):
                            r.set_lc(*lc)
                        tree.append(r)
                        break
                    if (rule, func) == last_items:
                        self.throw_error(
                            ErrorType.SYNTAX,
                            f"Invalid character: '{self.char}'",
                            char=self.char
                        )
        except LPV_Exception as e:
            raise e
        except Exception as e:
            if crash_handler is print:
                crash_handler(traceback.format_exc())
            else:
                crash_handler(e)
            self.throw_error(
                ErrorType.CRASH,
                "Uh oh. Looks like the lexer got an Python Error."
            )
        return TokenTree(self.source, *tree)