<!---
Where is v0.1-v1.9?

It's because of PyPi doesn't allow the same version on the same package.
When I upload the v0.1, I forgot to include __init__.py
and I had to change the version to another version in order to work

Why not just change it to v0.2/v1.0 instead of v2.0?

I forgor.
--->
v2.0
- Initial Release

v2.1
- Fixed LPV_Parser.eat issue

    `TypeError: sequence item 0: expected str instance, TokenType found`

    This happen when we do optional eat eg:

    `self.eat((TokenType("A"), TokenType("B")))`

    and the current token is not `A` or `B`.
    `eat` will just return an error but the error message
    expected to be: `Unexpected {self.token}, expected A or B` but instead, we just got the TypeError

- LPV_Lexer improvement

    - enter

        enter is now much safer. It will check if current character is none or not before
        adding it to the `self.chars`. It will also return all the characters that it added.
    
    - skip

        Same as `enter`

    - enter_if and skip_if

        this two function work like `LPV_Parser.eat`. If it doesn't get what it want,
        it just simply return an error
    
    - Remove `do_count_char` argument

        the LPV_Lexer has `do_count_char` argument. This is for counting how many character
        had been matched. This is useful if you have rule pattern that has different length.

        Eg: `["true","false","null"]`

        When the lexer match one of the word, then it going to call the rule function. The problem is, you don't know which word has been matched. It can be `true`, `false` or `null`. The solution for this problem is `self.match`. Your code probably going to looks like this:
        ```py
        if self.match("true"):
            return Token(TRUE, self.enter_clear(4))
        elif self.match("false"):
            return Token(FALSE, self.enter_clear(5))
        else:
            return Token(NULL, self.enter_clear(3))
        ```
        Although we can do this, it has performance issue.
        The issue is that it do `self.match` twice. We can change it to `self.match_string` instead but it still going to be slow. That's the reason the `do_count_char` do:
        ```py
        def __init__(self):
            self.rules = {...}
            super().__init__(do_count_char=True)
        ```
        ```py
        def lex_literal(self, length:int):
            self.enter(length)
            if self.chars == "true":
                ...
        ```
        but there's still one problem.

        If there's rule function that doesn't accept the length argument, then we just going to get `TypeError`. To fix this, we need to make all rules function to accept atleast one argument so we not going to get any error. Aren't that's annoying? That's why the LPV_Lexer don't need `do_count_char` argument anymore. If you want to get the match length, just add one argument to your rule function. It will automatically detect it and passed the length.