import enum
import math
import re
import sys
from typing import Optional

SUM_SUBTRACT_SIGN = ['-', '+']

class ParserException(Exception):
    line: int
    column: int
    message: str

    def __init__(self, line: int, column: int, message: str):
        self.line = line
        self.column = column
        self.message = message

    def __str__(self):
        return f"error: {self.message} on line {self.line} column {self.column}"


functions_supported = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'tanh': math.tanh,
    'sqrt': math.sqrt,
    'log2': math.log2,
    'log10': math.log10,
}


def generate_tokens(text: str):
    token_types = list(TokenType)

    token_regex = map(lambda t: f"(?P<{t.name}>{t.value[1]})", token_types)

    token_regex = "|".join(token_regex)

    regex = re.compile(token_regex)

    lines = text.split('\n')

    for i, line in enumerate(lines):
        scanner = regex.scanner(line)

        for m in iter(scanner.match, None):
            token_type = TokenType[m.lastgroup]
            tok = Token(token_type, m.group(), m.pos, i + 1)

            if token_type == TokenType.WS:
                continue

            yield tok


class TokenType(enum.Enum):
    NUMBER = ("NUMBER", "[+-]?([0-9]+(\\.[0-9]*)?|\\.[0-9]+)(e[0-9]+)?")
    IDENTIFIER = ("IDENTIFIER", "[a-zA-Z_]+([a-zA-Z0-9_])*")
    L_PARAM = ("LPARAM", "\\(")
    R_PARAM = ("RPARAM", "\\)")
    NEW_LINE = ("NEW_LINE", "\n")
    MULT = ("MULT", "\\*")
    POW = ("POW", "\\^")
    SUM = ("SUM", "\\+")
    SUBTRACT = ("SUB", "-")
    DIVIDE = ("DIV", "/")
    EQUAL = ("EQUAL", "=")
    WS = ("WS", " ")


class Token:
    token_type: TokenType
    value: any
    pos: int
    line: int

    def __init__(self, token_type: TokenType, value, pos: int, line: int):
        self.token_type = token_type
        self.value = value
        self.pos = pos
        self.line = line

    def __str__(self):
        return f"TokenType: {self.token_type} Value: {self.value} Position: {self.pos} Line: {self.line}"


class SymbolType(enum.Enum):
    FUNCTION = "FUNCTION"
    VARIABLE = "VARIABLE"


class Symbol:
    line_declaration: Optional[int]
    line_usage: Optional[int]
    typ: SymbolType
    value: object

    def __init__(self, typ, value, line_declaration=None, line_usage=None):
        self.typ = typ
        self.value = value
        self.line_declaration = line_declaration
        self.line_usage = line_usage


def create_symbol_table():
    symbol_table = {}

    for name, function in functions_supported.items():
        symbol_table[name] = Symbol(value=function, typ=SymbolType.FUNCTION)

    return symbol_table


class MathParser:
    text: str
    _current_line_: int
    _index_: int

    symbol_table: dict[str, Symbol]

    def __init__(self):
        self._tokens_ = None
        self.cache = []
        self._index_ = -1
        self._current_line_ = 1
        self.symbol_table = create_symbol_table()

    def _next_(self) -> Optional[Token]:
        try:
            self._current_token_ = next(self._tokens_)
            self.cache.append(self._current_token_)
        except StopIteration:
            self._current_token_ = None

        self._index_ += 1

        if self._index_ >= len(self.cache):

            return None

        return self.cache[self._index_]

    def _poke_(self):
        if self._index_ < 0:
            return

        self._index_ -= 1

        if self._index_ < 0 or len(self.cache) <= self._index_:
            return

        self._current_token_ = self.cache[self._index_]

    def _peek_(self, amount=1):
        token = None

        for _ in range(0, amount):
            token = self._next_()

        for _ in range(0, amount):
            self._poke_()

        return token

    def _reset_(self):
        self.cache = []
        self._index_ = -1

    @property
    def variables(self):
        variables = filter(lambda t: t[1].typ == SymbolType.VARIABLE, self.symbol_table.items())
        variables = map(lambda t: (t[0], t[1].value), variables)

        return dict(list(variables))

    def parse(self, text: str):
        self.text = text
        self._tokens_ = generate_tokens(text)
        self._reset_()

        return self._ea_()

    def _ea_(self):
        token = self._peek_()

        while token is not None:
            self._current_line_ = token.line
            next_token = self._peek_(2)

            if token.token_type == TokenType.IDENTIFIER and next_token.token_type == TokenType.EQUAL:
                self._assign_()
            else:
                return self._e_()

            token = self._peek_()

    def _e_(self):
        number = self._t_()
        token = self._next_()

        while token is not None:
            if token.token_type == TokenType.SUM:
                second = self._t_()
                number += second
            elif token.token_type == TokenType.SUBTRACT:
                second = self._t_()
                number -= second
            elif token.token_type == TokenType.NUMBER:
                sign = token.value[0]

                if sign not in SUM_SUBTRACT_SIGN:
                    self._unexpected_(token)

                self._poke_()
                second = self._t_()
                number += second
            else:
                self._poke_()
                break

            token = self._next_()

        return number

    def _t_(self):
        number = self._te_()
        token = self._next_()

        while token is not None:
            if token.token_type == TokenType.DIVIDE:
                second = self._te_()
                number /= second
            elif token.token_type == TokenType.MULT:
                second = self._te_()
                number *= second
            else:
                self._poke_()
                break

            token = self._next_()

        return number

    def _te_(self):
        number = self._f_()
        token = self._next_()
        while token is not None:
            if token.token_type == TokenType.POW:
                second = self._f_()
                number = pow(number, second) 
            else:
                self._poke_()
                break

            token = self._next_()

        return number

    def _fu_(self):
        token = self._expect_next(TokenType.IDENTIFIER)
        self._expect_next(TokenType.L_PARAM)

        number = self._e_()

        self._expect_next(TokenType.R_PARAM)

        function_name = token.value

        symbol = self.symbol_table.get(function_name)

        if symbol is None:
            self._raise_exception_(f"not found function with name: {function_name}")

        if symbol.typ != SymbolType.FUNCTION:
            self._raise_exception_(f"Expected function found {symbol.typ} that was declared on {symbol.line_declaration}")

        function = functions_supported[function_name]

        if function is None:
            self._not_supported_(f"function with name: {function_name}")

        return function(number)

    def _f_(self):
        token = self._next_()

        if token is None:
            self._expected_(TokenType.NUMBER)

        if token.token_type == TokenType.L_PARAM:
            result = self._e_()
            self._expect_next(TokenType.R_PARAM)

            return result
        elif token.token_type == TokenType.NUMBER:
            return float(token.value)
        elif token.token_type == TokenType.IDENTIFIER:
            next_token = self._peek_()

            if next_token is not None and next_token.token_type == TokenType.L_PARAM:
                self._poke_()
                return self._fu_()

            symbol = self.symbol_table.get(token.value)

            if symbol is None:
                self._raise_exception_(f"not found variable with name '{token.value}'")

            if symbol.typ != SymbolType.VARIABLE:
                self._raise_exception_(f"expected VARIABLE found '{symbol.typ}' with name '{token.value}'")

            return symbol.value

        self._unexpected_(token)

    def _assign_(self):
        identifier_token = self._expect_next(TokenType.IDENTIFIER)

        self._expect_next(TokenType.EQUAL)

        result = self._e_()

        symbol = self.symbol_table.get(identifier_token.value)

        if symbol is not None and symbol.typ != SymbolType.VARIABLE:
            self._raise_exception_(f"Can't create a variable with the name of a function: {identifier_token.value}")

        self.symbol_table[identifier_token.value] = Symbol(
            typ=SymbolType.VARIABLE,
            value=result,
            line_declaration=identifier_token.line
        )

    def _expect_next(self, token_type: TokenType) -> Token:
        token = self._next_()

        if token is None:
            self._expected_(token_type)
        elif token.token_type != token_type:
            self._unexpected_(token)

        return token

    def _unexpected_(self, token: Token):
        self._raise_exception_(f"unexpected token: {token}")

    def _get_line_info_(self):
        line = self._current_line_
        column = 0

        if self._current_token_ is not None:
            line = self._current_token_.line
            column = self._current_token_.pos

        return line, column

    def _expected_(self, token_type: TokenType):
        self._raise_exception_(f"missing token {token_type}")

    def _not_supported_(self, message: str):
        self._raise_exception_(f"not supported {message}")

    def _raise_exception_(self, message: str):
        line, column = self._get_line_info_()

        raise ParserException(line, column, message)


if __name__ == '__main__':
    p = MathParser()

    while True:
        line = sys.stdin.readline()
        res = p.parse(line)

        if res is not None:
            print(res)
        else:
            for key, value in p.variables.items():
                print(f"{key} = {value}")
