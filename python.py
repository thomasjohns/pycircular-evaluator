import sys
from typing import assert_never
from typing import Literal
from typing import NoReturn
from typing import Final


TokenKind = Literal[
    '(',
    ')',
    '[',
    ']',
    '{',
    '}',
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
    'instance_indent',
]

KEYWORDS: Final = [
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
    'enumerate',
    'max',
    'min',
    'self',
    'assert',
    'raise',
    'Exception',
    'SyntaxError',
    '__name__',
]

EOF: Final = 'EOF'


class Token:
    def __init__(
        self,
        line: int,
        col: int,
        kind: TokenKind,
        instance: str | None = None,
    ) -> None:
        self.line = line
        self.col = col
        self.kind = kind
        self.instance = instance

    def __repr__(self) -> str:
        if self.instance is None:
            if self.kind == 'instance_indent':
                return 'indent'
            else:
                return self.kind
        else:
            instance_kind = self.kind.removeprefix('instance_')
            return f'{instance_kind}({self.instance})'


class Lexer:
    def __init__(self, src: str) -> None:
        self.src = src
        self.pos = 0
        self.line = 1
        self.col = 1
        self.line_start = self.line
        self.col_start = self.col
        self.char: str = self.src[self.pos] if self.src else EOF
        self.tokens: list[Token] = []

    def push_token(self, kind: TokenKind, instance: str | None = None) -> None:
        token = Token(self.line_start, self.col_start, kind, instance)
        self.tokens.append(token)

    def eat(self) -> None:
        self.pos += 1
        self.col += 1
        if self.char == '\n':
            self.line += 1
            self.col = 1
            self.line_start = self.line
            self.col_start = self.col
        if self.pos < len(self.src):
            self.char = self.src[self.pos]
        else:
            self.char = EOF

    def peek(self) -> str | None:
        if self.pos + 1 < len(self.src):
            return self.src[self.pos + 1]
        else:
            return None

    def eat_expecting(self, expectation: str) -> None:
        fail_msg = f'{self.char} != {expectation} at line: {self.line}, col: {self.col}'
        assert self.char == expectation, fail_msg
        self.eat()

    def syntax_error_on_char(self) -> NoReturn:
        raise SyntaxError(
            f'Unexpected char {self.char} on line {self.line} in col {self.col}.'
        )

    def lex(self) -> list[Token]:
        while self.pos < len(self.src):
            self.line_start = self.line
            self.col_start = self.col
            match self.char:
                case '\n':
                    self.eat()
                    self.lex_indentation()
                case ' ':
                    self.eat()
                case '=':
                    match self.peek():
                        case '=':
                            self.push_token('==')
                            self.eat_expecting('=')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '%':
                    match self.peek():
                        case '=':
                            self.push_token('%=')
                            self.eat_expecting('%')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '+':
                    match self.peek():
                        case '=':
                            self.push_token('+=')
                            self.eat_expecting('+')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '*':
                    match self.peek():
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
                    match self.peek():
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
                    match self.peek():
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
                    match self.peek():
                        case '=':
                            self.push_token('>=')
                            self.eat_expecting('>')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '<':
                    match self.peek():
                        case '=':
                            self.push_token('<=')
                            self.eat_expecting('<')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case ':':
                    match self.peek():
                        case '=':
                            self.push_token(':=')
                            self.eat_expecting(':')
                            self.eat_expecting('=')
                        case _:
                            self.push_token(self.char)
                            self.eat()
                case '!':
                    match self.peek():
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
        self.push_token('instance_string', f'{start_char}{instance}{start_char}')
        self.eat_expecting(start_char)

    def lex_name_or_keyword(self) -> None:
        chars: list[str] = []
        while self.pos < len(self.src) and (
            self.char.isalpha() or self.char.isnumeric() or self.char == '_'
        ):
            chars.append(self.char)
            self.eat()
        instance = ''.join(chars)
        kind: Literal['instance_keyword', 'instance_name']
        if instance in KEYWORDS:
            kind = 'instance_keyword'
        else:
            kind = 'instance_name'
        self.push_token(kind, instance)

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
        for _ in range(num_indents):
            self.push_token('instance_indent')


def print_tokens(tokens: list[Token]) -> None:
    total_lines = max(token.line for token in tokens)
    line = 1
    while line <= total_lines:
        tokens_on_line = [token for token in tokens if token.line == line]
        space_separated_tokens = ' '.join(repr(token) for token in tokens_on_line)
        print(space_separated_tokens)
        line += 1


class GrowingLineBuffer:
    def __init__(self) -> None:
        self._data: list[list[str]] = []

    def insert(self, line: int, col: int, chars: str) -> None:
        while len(self._data) <= line:
            self._data.append([])
        while len(self._data[line - 1]) < col - 1 + len(chars):
            self._data[line - 1].append(' ')
        for i, char in enumerate(chars):
            self._data[line - 1][col - 1 + i] = char

    def __str__(self) -> str:
        return '\n'.join(''.join(char for char in line) for line in self._data)


def tokens_to_src(tokens: list[Token]) -> str:
    buff = GrowingLineBuffer()
    for token in tokens:
        match (token.lit, token.instance):
            case ('instance_comment', _):
                content = '#' + token.instance
            case ('instance_indent', _):
                content = '    '
            case (_, None):
                content = token.lit
            case (_, _):
                content = token.instance
        buff.insert(token.line, token.col, content)
    return str(buff)


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
    print('-' * 25, 'tokens back to source', '-' * 25)
    src = tokens_to_src(tokens)
    print(src)
    return 0


if __name__ == '__main__':
    _ = main()
