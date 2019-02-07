#! /usr/bin/env python

import argparse
import pprint
import string
import sys
import parsley

def calculate(start, pairs):
    result = start
    for op, value in pairs:
        if op == '+':
            result += value
        elif op == '-':
            result -= value
        elif op == '*':
            result *= value
        elif op == '/':
            result /= value
    return result

def make_token_grammar():
    """
    Make the token grammar.
    """
    grammar = parsley.makeGrammar("""
    digit = anything:x ?(x in '0123456789')
    number = <'-'{0, 1} digit+>:ds -> int(ds)
    itemlist = 
          ws item:first (ws item)*:rest ws -> [first] + rest
        | ws item:only ws -> [only]
    item =
          itemlist
        | '[' ws itemlist:lst ws ']' -> lst
        | '[' ws ']' -> []
        | word:w (ws comment)* -> w
        | '(' itemlist:lst ')' -> lst 
    word = expr | <(word_char+)>:val -> val
    ascii_lower = :x ?(x in 'abcdefghijklmnopqrstuvwxyz') -> x
    ascii_upper = :x ?(x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') -> x
    ascii = ascii_lower | ascii_upper
    identifier_char = ascii | digit | '.'
    punctuation = :x ?(x in "+-*/!'#$%&\,.:<=>?@^_`" '"')
    word_char = ascii | digit | punctuation
    comment = ';' rest_of_line 
    rest_of_line = <('\\\\n' | (~'\\n' anything))*>
    parens = '(' ws expr:e ws ')' -> e
    value = number | parens
    add = '+' ws expr2:n -> ('+', n)
    sub = '-' ws expr2:n -> ('-', n)
    mul = '*' ws value:n -> ('*', n)
    div = '/' ws value:n -> ('/', n)

    addsub = ws (add | sub)
    muldiv = ws (mul | div)

    expr = expr2:left addsub*:right -> calculate(left, right)
    expr2 = value:left muldiv*:right -> calculate(left, right)
    """, {"calculate": calculate})
    return grammar

def parse_tokens(grammar, script):
    """
    Parse a Logo script.
    Return a list of tokens.
    """
    return grammar(script).itemlist()

def main(args):
    """
    Parse Logo
    """
    grammar = make_token_grammar()
    if args.tests:
        print("Tests ...")
        tests = [
            'print hello world',
            'print [hello world]',
            'print [hello [nested] world]',
            'line1\nline2',
            'to circle :radius\narc 360 :radius\nend',
            'print "hello',
            'print "hello;this is a comment\nshow [a list]',
            'print (2 + 3) * 5',
            'to equalateral :side [:colors []]',
            'localmake "colors (list :color :color :color)',
            'make "theta heading * -1 + 90'
        ]
        for prog in tests:
            print(parse_tokens(grammar, prog))
        print("Tests completed.")
    script = args.file.read()
    print(parse_tokens(grammar, script))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logo programming language interpreter")
    parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Logo script file to interpret.")
    parser.add_argument(
        "-t",
        "--tests",
        action="store_true",
        help="Run preliminary tests.")
    args = parser.parse_args()
    main(args)
