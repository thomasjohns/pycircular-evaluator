from textwrap import dedent

import pytest

from python import Lexer
from python import print_tokens


@pytest.mark.parametrize('src,expected_printed_tokens', [
    (
        dedent('''\
            class Multiplication:
                def __init__(self, left: int, right: int) -> None:
                    self.left = left
                    self.right = right

                def compute(self) -> int:
                    return self.left * self.right


            def main():
                if Multiplication(2, 3).compute() >= 10:
                    print('hello world')
                else:
                    print('hello Mars')


            main()'''
        ),
        dedent('''\
            keyword(class) name(Multiplication) :
            indent keyword(def) name(__init__) ( keyword(self) , name(left) : keyword(int) , name(right) : keyword(int) ) -> keyword(None) :
            indent indent keyword(self) . name(left) = name(left)
            indent indent keyword(self) . name(right) = name(right)

            indent keyword(def) name(compute) ( keyword(self) ) -> keyword(int) :
            indent indent keyword(return) keyword(self) . name(left) * keyword(self) . name(right)


            keyword(def) name(main) ( ) :
            indent keyword(if) name(Multiplication) ( name(2) , name(3) ) . name(compute) ( ) >= name(10) :
            indent indent keyword(print) ( string(hello world) )
            indent keyword(else) :
            indent indent keyword(print) ( string(hello Mars) )


            name(main) ( )'''
       ),
    ),
])
def test_lex_program(src, expected_printed_tokens, capsys):
    lexer = Lexer(src)
    tokens = lexer.lex()
    print_tokens(tokens)
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_printed_tokens.strip()
