import sys
from typing import Literal


TokenLiteral = Literal[
    '(',
    ')',
    '[',
    ']',
    '{',
    '{',
    '=',
    '==',
    '>',
    '<',
    '/',
    '//',
    '+',
    '-',
    '*',
    '%',
    '#',
    '**',
    '>=',
    '<=',
    '+=',
    '-=',
    '/=',
    '*=',
    '->',
    '|',
    ':',
    '\'',
    '"',
    '.',
    ',',
    'f',
    '_',
    'instance_keyword',
    'instance_string',
    'instance_name',
    'instance_comment',
    'instance_type_annotation',
    'instance_indent',
]

KEYWORDS = [
    'if',
    'else',
    'elif',
    'match',
    'for',
    'while',
    'is',
    'as',
    'def',
    'class',
    'return',
    'from',
    'import',
    'None',
    'True',
    'False',
    'print',
    'with',
    'open',
    'str',
    'len',
    'range',
    'self',
    'assert',
    'raise',
    'Exception',
    'SyntaxError',
    '__name__',
]


class Token:
    def __init__(self, lit: TokenLiteral, instance: str | None = None) -> None:
        self.lit = lit
        self.instance = instance

    def __repr__(self):
        if self.instance is None:
            if self.lit == 'instance_indent':
                return 'indent'
            else:
                return self.lit
        else:
            instance_kind = self.lit.removeprefix('instance_')
            return f'{instance_kind}({self.instance})'


class Lexer:
    def __init__(self, src: str) -> None:
        self.src = src
        self.pos = 0
        self.col = 1
        self.line = 1
        self.char: str | None = self.src[self.pos] if self.src else None
        self.tokens: list[Token] = []

    def eat(self) -> None:
        self.pos += 1
        self.col += 1
        if self.char == '\n':
            self.line += 1
            self.col = 1
        if self.pos < len(self.src):
            self.char = self.src[self.pos]
        else:
            self.char = None

    def eat_expecting(self, expectation: str) -> None:
        assert self.char == expectation
        self.eat()

    def lex(self) -> list[Token]:
        while self.pos < len(self.src):
            match self.char:
                case '\n':
                    self.eat()
                    self.lex_indentation()
                case ' ':
                    self.eat()
                case '(' | ')' | ':':
                    token = Token(self.char)
                    self.tokens.append(token)
                    self.eat()
                case '\'' | '"':
                    self.lex_string(start_char=self.char)
                case str():
                    self.lex_name_or_keyword()
                case _:
                    raise SyntaxError(
                        f'Unexpected char {self.char} on line {self.line} in col {self.col}.'
                    )
        return self.tokens

    def lex_string(self, start_char: Literal['\'', '"']) -> None:
        chars: list[str] = []
        self.eat()
        while self.char != start_char:
            chars.append(self.char)
            self.eat()
        instance = ''.join(chars)
        token = Token('instance_string', instance)
        self.tokens.append(token)
        self.eat_expecting(start_char)

    def lex_name_or_keyword(self) -> None:
        chars: list[str] = []
        while self.pos < len(self.src) and (
            self.char.isalpha() or self.char.isnumeric() or self.char == '_'
        ):
            chars.append(self.char)
            self.eat()
        instance = ''.join(chars)
        if instance in KEYWORDS:
            token = Token('instance_keyword', instance)
        else:
            token = Token('instance_name', instance)
        self.tokens.append(token)

    def lex_indentation(self) -> None:
        # NOTE: We assume 4 for now :)
        num_spaces = 0
        while self.char == ' ':
            num_spaces += 1
            self.eat()
        if num_spaces % 4 != 0:
            raise SyntaxError(
                f'Unexpected indent on line {self.line}.'
            )
        num_indents = num_spaces // 4
        for indent in range(num_indents):
            token = Token('instance_indent')
            self.tokens.append(token)



def main() -> int:
    source_file = sys.argv[-1]
    with open(source_file, 'r') as fp:
        src = fp.read()
        print(src)
        lexer = Lexer(src)
    tokens = lexer.lex()
    for token in tokens:
        print(token)
    return 0


if __name__ == '__main__':
    main()
