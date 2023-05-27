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
    '%=',
    '!=',
    '->',
    '|',
    ':',
    ':=',
    "'",
    '"',
    '.',
    ',',
    'f',
    '_',
    'instance_keyword',
    'instance_string',
    'instance_number',
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
    'case',
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
    'int',
    'float',
    'str',
    'repr',
    'len',
    'range',
    'max',
    'min',
    'self',
    'assert',
    'raise',
    'Exception',
    'SyntaxError',
    '__name__',
]


class Token:
    def __init__(
        self,
        line: int,
        col: int,
        lit: TokenLiteral,
        instance: str | None = None,
    ) -> None:
        self.line = line
        self.col = col
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
        self.line = 1
        self.col = 1
        self.char: str | None = self.src[self.pos] if self.src else None
        self.tokens: list[Token] = []

    def push_token(self, lit: TokenLiteral, instance: str | None = None) -> None:
        token = Token(self.line, self.col, lit, instance)
        self.tokens.append(token)

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

    def peek(self) -> str | None:
        if self.pos + 1 < len(self.src):
            return self.src[self.pos + 1]
        else:
            return None

    def eat_expecting(self, expectation: str) -> None:
        fail_msg = f'{self.char} != {expectation} at line: {self.line}, col: {self.col}'
        assert self.char == expectation, fail_msg
        self.eat()

    def syntax_error_on_char(self) -> None:
        raise SyntaxError(
            f'Unexpected char {self.char} on line {self.line} in col {self.col}.'
        )

    def lex(self) -> list[Token]:
        while self.pos < len(self.src):
            match self.char:
                case '\n':
                    self.eat()
                    self.lex_indentation()
                case ' ':
                    self.eat()
                case '=':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('==')
                            self.eat_expecting('=')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '%':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('%=')
                            self.eat_expecting('%')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '+':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('+=')
                            self.eat_expecting('+')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '*':
                    match (next_char := self.peek()):
                        case '*':
                            self.push_token('**')
                            self.eat_expecting('*')
                            self.eat_expecting('*')
                        case '=':
                            self.push_token('*=')
                            self.eat_expecting('*')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '/':
                    match (next_char := self.peek()):
                        case '/':
                            self.push_token('//')
                            self.eat_expecting('/')
                            self.eat_expecting('/')
                        case '=':
                            self.push_token('/=')
                            self.eat_expecting('/')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '-':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('-=')
                            self.eat_expecting('=')
                        case '>':
                            self.push_token('->')
                            self.eat()
                            self.eat_expecting('>')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '>':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('>=')
                            self.eat_expecting('>')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '<':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('<=')
                            self.eat_expecting('<')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case ':':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token(':=')
                            self.eat_expecting(':')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '!':
                    match (next_char := self.peek()):
                        case '=':
                            self.push_token('!=')
                            self.eat_expecting('!')
                            self.eat_expecting('=')
                        case _:
                            self.syntax_error_on_char()
                case '|' | '{' | '}' | '[' | ']' | '(' | ')' | '.' | ',':
                    self.push_token(self.char)
                    self.eat()
                case "'" | '"':
                    self.lex_string(start_char=self.char)
                case s if s.isalpha() or s.isnumeric() or s == '_':
                    self.lex_name_or_keyword()
                case i if i.isnumeric():
                    self.lex_number()
                case '#':
                    self.lex_comment()
                case _:
                    self.syntax_error_on_char()
        return self.tokens

    def lex_string(self, start_char: Literal["'", '"']) -> None:
        chars: list[str] = []
        self.eat()
        while self.char != start_char:
            chars.append(self.char)
            self.eat()
        instance = ''.join(chars)
        self.push_token('instance_string', instance)
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
            lit = 'instance_keyword'
        else:
            lit = 'instance_name'
        self.push_token(lit, instance)

    def lex_number(self) -> None:
        chars: list[str] = []
        while self.pos < len(self.src) and (self.char.isnumeric() or self.char == '.'):
            chars.append(self.char)
            self.eat()
        instance = ''.join(chars)
        self.push_token('instance_number', instance)

    def lex_comment(self) -> None:
        self.eat_expecting('#')
        chars: list[str] = []
        while self.pos < len(self.src) and self.char != '\n':
            chars.append(self.char)
            self.eat()
        instance = ''.join(chars)
        self.push_token('instance_comment', instance)

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
            self.push_token('instance_indent')


def print_tokens(tokens: list[Token]) -> str:
    total_lines = max(token.line for token in tokens)
    line = 1
    while line <= total_lines:
        tokens_on_line = [token for token in tokens if token.line == line]
        space_separated_tokens = ' '.join(repr(token) for token in tokens_on_line)
        print(space_separated_tokens)
        line += 1


def main() -> int:
    source_file = sys.argv[-1]
    with open(source_file, 'r') as fp:
        src = fp.read()
    print('-' * 25, 'source', '-' * 25)
    print(src)
    lexer = Lexer(src)
    tokens = lexer.lex()
    print('-' * 25, 'tokens', '-' * 25)
    print_tokens(tokens)
    # TODO create token to code printer, then test code to token' to code' to token'' to code''
    #      and assert code' == code'' where code = python.py
    #      and assert token' == token''
    return 0


if __name__ == '__main__':
    main()
