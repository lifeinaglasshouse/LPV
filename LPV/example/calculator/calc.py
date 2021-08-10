from LPV import ErrorType
from LPV import LPV_Exception
from LPV import (LPV_Lexer,
                 Token,
                 TokenType)
from LPV import LPV_Parser, Node, NodeVisitor

class ERROR(ErrorType):
    MATH = "MathError"

class T_type:
    LITERAL = TokenType('LITERAL')
    PLUS, MINUS, MULT, DIV = (
        TokenType('PLUS'), 
        TokenType('MINUS'), 
        TokenType('MULT'),
        TokenType('DIV')
    )
    LPAREN = TokenType('LPAREN')
    RPAREN = TokenType('RPAREN')

class Lexer(LPV_Lexer):

    def __init__(self):
        self.DIGIT = lambda c: c.isdigit()
        self.WS = lambda c: c.isspace()
        self.rules = (
            (self.WS, self.lex_whitespace),
            (self.DIGIT, self.lex_num),
            (["+", "-", "*", "/"], self.lex_op),
            (["(", ")"], self.lex_paren)
        )
        super().__init__()

    def lex_whitespace(self):
        self.skip_while(self.WS)
        return None

    def lex_num(self):
        self.enter_while(self.DIGIT)
        if self.char == ".":
            self.enter()
            self.enter_while(self.DIGIT)
            return Token(T_type.LITERAL, float(self.clear()))
        return Token(T_type.LITERAL, int(self.clear()))

    def lex_op(self):
        self.enter()
        if self.chars == "+":
            return Token(T_type.PLUS, self.clear())
        if self.chars == "-":
            return Token(T_type.MINUS, self.clear())
        if self.chars == "*":
            return Token(T_type.MULT, self.clear())
        if self.chars == "/":
            return Token(T_type.DIV, self.clear())

    def lex_paren(self):
        if self.char == "(":
            self.enter()
            return Token(T_type.LPAREN, self.clear())
        self.enter()
        return Token(T_type.RPAREN, self.clear())

class Parser(LPV_Parser):

    def __init__(self):
        self.start = self.parse_expr, ()
        super().__init__()

    def parse_factor(self):
        lc = self.get_lc()
        if self.token == T_type.LITERAL:
            return LiteralValue(
                self.eat().value,
                *lc
            )
        elif self.check_type((T_type.PLUS, T_type.MINUS)):
            return UnaryOp(
                self.eat(),
                self.parse_expr(),
                *lc
            )
        elif self.token == T_type.LPAREN:
            self.eat()
            node = self.parse_expr()
            self.eat(T_type.RPAREN)
            return node
        else:
            msg = "Unexpected "
            if self.is_eof():
                msg += "EOF"
            else:
                msg += f"'{self.token.value}'"
            self.throw_error(
                ERROR.SYNTAX,
                msg+", expected valid expression"
            )
    
    def parse_term(self):
        lc = self.get_lc()
        node = self.parse_factor()
        while self.check_type((T_type.MULT,T_type.DIV)):
            node = BinOp(
                node,
                self.eat(),
                self.parse_factor(),
                *lc
            )
        return node
    
    def parse_expr(self):
        lc = self.get_lc()
        node = self.parse_term()
        while self.check_type((T_type.PLUS,T_type.MINUS)):
            node = BinOp(
                node,
                self.eat(),
                self.parse_term(),
                *lc
            )
        return node   

class BinOp(Node):
    
    def __init__(self, left:Node, op:Token, right:Node, line: int, col: int):
        self.left, self.op, self.right = left, op, right
        super().__init__(line, col=col)
        
class LiteralValue(Node):
    
    def __init__(self, value, line: int, col: int):
        self.value = value
        super().__init__(line, col=col)

class UnaryOp(Node):
    
    def __init__(self, left:Token, right:Node, line: int, col: int):
        self.left, self.right = left, right
        super().__init__(line, col=col)

class Interpreter(NodeVisitor):
    
    def visit_BinOp(self, node: BinOp):
        left, right = self.visits(node.left, node.right)
        if node.op == T_type.PLUS:
            return left+right
        if node.op == T_type.MINUS:
            return left-right
        if node.op == T_type.MULT:
            return left*right
        if node.op == T_type.DIV:
            return left/right
    
    def visit_LiteralValue(self, node: LiteralValue):
        return node.value
    
    def visit_UnaryOp(self, node: UnaryOp):
        right = self.visit(node.right)
        if node.left == T_type.PLUS:
            return +right
        if node.left == T_type.MINUS:
            return -right
calc_lexer, calc_parser, calc = Lexer(), Parser(), Interpreter()

def do_nothing(_):
    pass

def calculate(math: str, ignore_error_crash:bool=True):
    handler = print if ignore_error_crash is False else do_nothing
    if math and not math.isspace():
        return calc.run(
            calc_parser.parse(
                calc_lexer.lex(
                    math, crash_handler=handler
                ), handler
            ), math, handler
        )

if __name__ == "__main__":
    while True:
        try:
            code = input(">>> ")
            if code and not code.isspace():
                t_tree = calc_lexer.lex(code)
                n_tree = calc_parser.parse(t_tree)
                print(calc.run(n_tree, code))
        except LPV_Exception as e:
            print(e)
        except (KeyboardInterrupt, EOFError):
            break
