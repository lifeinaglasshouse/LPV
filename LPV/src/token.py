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
from typing import Iterable

class TokenType:
    
    def __init__(self, name: str) -> None:
        self.name = name
    def __repr__(self):
        return self.name
    def __eq__(self, o: str):
        return self.name == o

class Token:
    
    def __init__(self, type_: TokenType, value) -> None:
        if not isinstance(type_, TokenType):
            raise TypeError(
                f"type_ argument must be TokenType not {type(type_).__name__}"
            )
        self.type, self.value = type_, value
        self.line, self.col = None, None
    def set_lc(self, line:int, col:int):
        self.line, self.col = line, col
    def __repr__(self) -> str:
        return "Token({type}, '{value}')".format(
            type=self.type,value=self.value
        )
    def __eq__(self, o: object) -> bool:
        return (self.type == o) if isinstance(o, TokenType) else (self.value == o)

def generate_tokens(name: str, tokens: Iterable[str], build:bool=False):
    if not name.isidentifier():
        raise TypeError(
                f"Invalid class name: {name}"
            )
    for t in tokens:
        if not t.isidentifier():
            raise TypeError(
                f"Invalid token name: {t}"
            )
    code = """\
class {name}:
{attributes}\
""".format(
            name=name,
            attributes="\n".join(
                (f"    {t} = TokenType('{t}')" for t in tokens)
            )
        )
    if build is True:
        return code
    exec(code)
    return eval(name)

class TokenTree:
    
    def __init__(self, source: str, *tokens: Token) -> None:
        self.source = source
        self.tokens, self.len_t = tokens, len(tokens)
        self.pos, self.token = -1, None
        self.line, self.col = 0, 0
    
    def __getitem__(self, index):
        return self.tokens[index]
    
    def next_token(self):
        self.pos += 1
        if self.pos >= self.len_t:
            self.token = None
            return self.token
        else:
            self.token = self.tokens[self.pos]
            self.line, self.col = self.token.line, self.token.col
            return self.token
    
    def peek(self, step:int=1):
        p = self.pos+step
        if p >= self.len_t:
            return None
        return self.tokens[p]
    
    def get(self, o: object, default=None):
        for t in self.tokens:
            if t == o:
                return t
        return default
    
    def __repr__(self):
        string = "TokenTree:\n"
        space = " "*len(string[:-1])
        for token in self.tokens:
            head = f"{token.type}:"
            content = f"{' '*len(head)}\"{token.value}\""
            string += space+head+"\n"+space+content+"\n"
        return string