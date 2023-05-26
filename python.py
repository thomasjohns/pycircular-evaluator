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
    'instance_keyword',
    'instance_string',
    'instance_name',
    'instance_comment',
    'instance_type_annotation',
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
    'print',
    'with',
    'open',
    'str',
    'len',
    'self',
    'assert',
    '__name__',
]


class Token:
    def __init__(self, lit: TokenLiteral, instance: str | None = None) -> None:
        self.lit = lit
        self.instance = instance

    def __repr__(self):
        if self.instance is not None:
            instance_kind = self.lit.removeprefix('instance_')
            return f'{instance_kind}({self.instance})'
        else:
            return self.lit


class Lexer:
    def __init__(self, src: str) -> None:
        self.src = src
        self.pos = 0
        self.char: str | None = self.src[self.pos] if self.src else None
        self.tokens: list[Token] = []

    def eat(self) -> None:
        self.pos += 1
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
                case '(' | ')':
                    token = Token(self.char)
                    self.tokens.append(token)
                    self.eat()
                case '\'' | '"':
                    self.lex_string(start_char=self.char)
                case str():
                    self.lex_name_or_keyword()
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


def main() -> int:
    source_file = sys.argv[-1]
    with open(source_file, 'r') as fp:
        src = fp.read()
        print(src)
        lexer = Lexer(src)
    tokens = lexer.lex()
    print(tokens)
    return 0


if __name__ == '__main__':
    main()
