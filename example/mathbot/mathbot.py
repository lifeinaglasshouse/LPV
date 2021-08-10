from LPV import (
    LPV_Lexer, Token, TokenType,
    LPV_Exception, LPV_Parser,
    ErrorType
)

class Error(ErrorType):
    MATH = "MathError"

class t_type:
    NUMBER = TokenType('NUMBER')
    PLUS = TokenType('PLUS')
    MINUS = TokenType('MINUS')
    MULT = TokenType('MULT')
    DIV = TokenType('DIV')

class Lexer(LPV_Lexer):
    
    
    def __init__(self):
        self.DIGIT = lambda c: c.isdigit()
        self.WS = lambda c: c.isspace()
        self.rules = (
            (self.DIGIT, self.lex_number),
            (self.WS, self.lex_whitespace),
            ({"add","plus","sub","minus","mult","div"}, 
            self.lex_keyword),
            (lambda _:True, self.lex_other)
        )
        super().__init__(do_count_char=True)
    
    def lex_number(self, _):
        self.enter_while(self.DIGIT)
        if self.char == ".":
            self.enter()
            self.enter_while(self.DIGIT)
            return Token(t_type.NUMBER, float(self.clear()))
        return Token(t_type.NUMBER, int(self.clear()))
    
    def lex_whitespace(self, _):
        self.skip_while(self.WS)
    
    def lex_keyword(self, len_:int):
        self.enter(len_)
        s = self.chars.lower()
        if s in ("add","plus"):
            return Token(t_type.PLUS, self.clear())
        if s in ("sub","minus"):
            return Token(t_type.MINUS, self.clear())
        if s == "mult":
            return Token(t_type.MULT, self.clear())
        if s == "div":
            return Token(t_type.DIV, self.clear())

    def lex_other(self, _):
        self.skip()

class Parser(LPV_Parser):
    
    def __init__(self):
        self.start = self.parse_satisfy, ()
        super().__init__()
        
    def parse_satisfy(self):
        num1, num2, op = None, None, None
        while not self.is_eof() and None in (num1,num2,op):
            if self.token == t_type.NUMBER:
                if num1 is None:
                    num1 = self.eat().value
                    continue
                if num2 is None:
                    num2 = self.eat().value
            else:
                if op is None:
                    op = self.eat()
        if None in (num1,num2,op):
            self.throw_error(
                Error.SYNTAX, "Invalid Syntax"
            )
        return self.parse_exec(num1,num2,op)
    
    def parse_exec(self, num1, num2, op):
        if op == t_type.PLUS:
            return num1+num2
        if op == t_type.MINUS:
            return num1-num2
        if op == t_type.MULT:
            return num1*num2
        if op == t_type.DIV:
            if num2 == 0:
                self.throw_error(
                    Error.MATH,
                    "Can't divide by zero"
                )
            return num1/num2

if __name__ == "__main__":
    lexer, parser = Lexer(), Parser()
    while True:
        try:
            code = input("MathBot> ")
            if code and not code.isspace():
                t = lexer.lex(code)
                print(parser.parse(t))
        except LPV_Exception as e:
            if e.error == Error.SYNTAX:
                print("Sorry, I do not understand")
            elif e.error == Error.MATH:
                print("I don't know the answer")
        except (KeyboardInterrupt, EOFError):
            break