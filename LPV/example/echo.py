from LPV import (
    LPV_Lexer, LPV_Parser, Token, TokenType,
    LPV_Exception
)

class t_type:
    ECHO = TokenType("ECHO")
    STRING = TokenType("STRING")

class Lexer(LPV_Lexer):
    
    def __init__(self):
        self.WS = lambda c: c.isspace()
        self.rules = (
            ("echo", self.lex_echo),
            (['"',"'"], self.lex_str),
            (self.WS, self.lex_whitespace)
        )
        super().__init__()
    
    def lex_echo(self):
        return Token(t_type.ECHO, self.enter_clear(4))
    
    def lex_str(self):
        p = self.char
        self.skip()
        self.enter_while(lambda c: c != p)
        self.skip()
        return Token(t_type.STRING, self.clear())
    
    def lex_whitespace(self):
        self.skip_while(self.WS)

class Parser(LPV_Parser):
    
    def __init__(self):
        self.start = self.parse_echo, ()
        super().__init__()
        
    def parse_echo(self):
        self.eat(t_type.ECHO)
        print(self.eat(t_type.STRING).value)

if __name__ == "__main__":
    l, p = Lexer(), Parser()
    while True:
        try:
            code = input(">>> ")
            if code and not code.isspace():
                t_tree = l.lex(code)
                p.parse(t_tree)
        except LPV_Exception as e:
            print(e)
        except (KeyboardInterrupt, EOFError):
            break