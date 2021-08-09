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

class ErrorType:
    SYNTAX = "SyntaxError"
    CRASH = "UnexpectedPythonError"

class LPV_Exception(Exception):
    
    def __init__(self, **kwargs):
        """
        Kwargs:
            error: str
            msg: str
            line: int
            col: int | optional
            source: str
            pointer_width: int | optional
            when: str | optional
        """
        self.error:str = kwargs.pop("error")
        self.msg:str = kwargs.pop("msg")
        self.line:int = kwargs.pop("line")
        self.col:int = kwargs.pop("col") if "col" in kwargs else None
        self.source:str = kwargs.pop("source")
        self.pointer_width:int = kwargs.pop("pointer_width") if "pointer_width" in kwargs else 1
        self.when:str = kwargs.pop("when") if "when" in kwargs else None
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        super().__init__(self.__repr__())
        
    def __repr__(self):
        ln = self.line+1
        s_ln = len(str(ln))
        ln_str = self.source.splitlines()[self.line]
        string = "An Error Has Occurred:" if self.when is None else f"{self.when}::Error Occurred:"
        string += "\n  "+("─"*s_ln)+"──┬─"+("─"*len(ln_str))+"─"
        string += "\n   {ln} │ {ln_str} ".format(
            ln=ln, ln_str=ln_str,
        )
        col = "\n"
        if self.col is not None:
            col = "\n   {ln_len} │ {space}{pointer}─┤col:{col}│".format(
                ln_len=" "*s_ln, space=" "*self.col,
                col=self.col+1,
                pointer="└"+("┴"*(self.pointer_width-1)),
            )
        string += col
        return string+f"\n{self.error}: {self.msg}"