from __future__ import annotations

import sys
from typing import assert_never
from typing import Final
from typing import Literal
from typing import NoReturn
from typing import TypeAlias
from typing import Union


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
        match (token.kind, token.instance):
            case ('instance_comment', _):
                assert token.instance is not None
                content = '#' + token.instance
            case ('instance_indent', _):
                content = '    '
            case (_, None):
                content = token.kind
            case (_, _):
                assert token.instance is not None
                content = token.instance
        buff.insert(token.line, token.col, content)
    return str(buff)


ExprContext = Literal['load', 'store', 'del']


class Module:
    def __init__(self, body: list[Stmt]) -> None:
        self.body = body


class Arg:
    def __init__(self, name: str, arg_type: Expr | None) -> None:
        self.name = name
        self.arg_type = arg_type


class FunArgs:
    def __init__(self, args: list[Arg], defaults: list[Expr]) -> None:
        self.args = args
        self.defaults = defaults


class FunDef:
    def __init__(
        self,
        name: str,
        args: FunArgs,
        body: list[Stmt],
        return_type: Expr | None,
    ) -> None:
        self.name = name
        self.args = args
        self.body = body
        self.return_type = return_type


class ClassDef:
    def __init__(self, name: str, body: list[Stmt]) -> None:
        self.name = name
        self.body = body


class Return:
    def __init__(self, value: Expr | None) -> None:
        self.value = value


class Assign:
    def __init__(self, target: Expr, value: Expr, assign_type: Expr | None) -> None:
        self.target = target
        self.value = value
        self.assign_type = assign_type


class For:
    def __init__(self, target: Expr, iter_expr: Expr, body: list[Stmt]) -> None:
        self.target = target
        self.iter_expr = iter_expr
        self.body = body


class While:
    def __init__(self, test: Expr, body: list[Stmt]) -> None:
        self.test = test
        self.body = body


class If:
    def __init__(self, test: Expr, body: list[Stmt]) -> None:
        self.test = test
        self.body = body


class With:
    # TODO
    ...


class Match:
    # TODO
    ...


class Raise:
    # TODO
    ...


class Try:
    # TODO
    ...


class Assert:
    # TODO
    ...


class Import:
    # TODO
    ...


class Break:
    ...


class Continue:
    ...


class Pass:
    ...


BoolOpOp = Literal['and', 'or']
BinOpOp = Literal['+', '-', '*', '/', '%', '**']
UnaryOpOp = Literal['+', '-', 'not']
CompOpOp = Literal['==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in']


class BoolOp:
    def __init__(self, left: Expr, op: BoolOpOp, right: Expr) -> None:
        self.left = left
        self.op = op
        self.right = right


class BinOp:
    def __init__(self, left: Expr, op: BinOpOp, right: Expr) -> None:
        self.left = left
        self.op = op
        self.right = right


class UnaryOp:
    def __init__(self, op: UnaryOpOp, operand: Expr) -> None:
        self.op = op
        self.operand = operand


class IfExp:
    # TODO
    ...


class Dict:
    # TODO
    ...


class Set:
    # TODO
    ...


class ListComp:
    # TODO
    ...


class SetComp:
    # TODO
    ...


class DictComp:
    # TODO
    ...


class CompOp:
    def __init__(self, left: Expr, op: CompOpOp, right: Expr) -> None:
        self.left = left
        self.op = op
        self.right = right


class KeyWord:
    def __init__(self, name: str, value: Expr) -> None:
        self.name = name
        self.value = value


class Call:
    def __init__(self, func: Name, args: list[Expr], keywords: list[KeyWord]) -> None:
        self.func = func
        self.args = args
        self.keywords = keywords


class FormattedValue:
    # TODO
    ...


class JoinedStr:
    # TODO
    ...


class Attribute:
    def __init__(self, value: Expr, attr: str, ctx: ExprContext) -> None:
        self.value = value
        self.attr = attr
        self.ctx = ctx


class Name:
    def __init__(self, lit: str, ctx: ExprContext) -> None:
        self.lit = lit
        self.ctx = ctx


class List:
    # TODO
    ...


class Tuple:
    # TODO
    ...


class Slice:
    # TODO
    ...


class Int:
    def __init__(self, lit: int) -> None:
        self.lit = lit


class Float:
    def __init__(self, lit: float) -> None:
        self.lit = lit


class Str:
    def __init__(self, lit: str, quote_style: Literal['"', "'"]) -> None:
        self.lit = lit
        self.quote_style = quote_style


Constant: TypeAlias = Union[Int, Float, Str]

Stmt: TypeAlias = Union[
    Arg,
    FunArgs,
    FunDef,
    ClassDef,
    Return,
    Assign,
    For,
    While,
    If,
    With,
    Match,
    Raise,
    Try,
    Assert,
    Import,
    Break,
    Continue,
    Pass,
]

Expr: TypeAlias = Union[
    BoolOp,
    BinOp,
    UnaryOp,
    IfExp,
    Dict,
    Set,
    ListComp,
    SetComp,
    DictComp,
    CompOp,
    KeyWord,
    Call,
    FormattedValue,
    JoinedStr,
    Attribute,
    Name,
    List,
    Tuple,
    Slice,
    Constant,
]

Node: TypeAlias = Union[Module, Stmt, Expr]


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens

    def parse(self) -> Node:
        # TODO
        for token in self.tokens:
            match token:
                case _:
                    pass
        return Int(42)


class CodePrinter:
    def __init__(self, node: Node) -> None:
        self.node = node

    def pprint(self) -> None:
        match self.node:
            case Module():
                # TODO
                pass
            case Arg():
                # TODO
                pass
            case FunArgs():
                # TODO
                pass
            case FunDef():
                # TODO
                pass
            case ClassDef():
                # TODO
                pass
            case Return():
                # TODO
                pass
            case Assign():
                # TODO
                pass
            case For():
                # TODO
                pass
            case While():
                # TODO
                pass
            case If():
                # TODO
                pass
            case With():
                # TODO
                pass
            case Match():
                # TODO
                pass
            case Raise():
                # TODO
                pass
            case Try():
                # TODO
                pass
            case Assert():
                # TODO
                pass
            case Import():
                # TODO
                pass
            case Break():
                # TODO
                pass
            case Continue():
                # TODO
                pass
            case Pass():
                # TODO
                pass
            case BoolOp():
                # TODO
                pass
            case BinOp():
                # TODO
                pass
            case UnaryOp():
                # TODO
                pass
            case IfExp():
                # TODO
                pass
            case Dict():
                # TODO
                pass
            case Set():
                # TODO
                pass
            case ListComp():
                # TODO
                pass
            case SetComp():
                # TODO
                pass
            case DictComp():
                # TODO
                pass
            case CompOp():
                # TODO
                pass
            case KeyWord():
                # TODO
                pass
            case Call():
                # TODO
                pass
            case FormattedValue():
                # TODO
                pass
            case JoinedStr():
                # TODO
                pass
            case Attribute():
                # TODO
                pass
            case Name():
                # TODO
                pass
            case List():
                # TODO
                pass
            case Tuple():
                # TODO
                pass
            case Slice():
                # TODO
                pass
            case Int():
                # TODO
                pass
            case Float():
                # TODO
                pass
            case Str():
                # TODO
                pass
            case _:  # pyright: ignore
                assert_never(self.node)


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
