#! /usr/bin/env python

import argparse
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

def main(args):
    """
    Parse Logo
    """
    grammar = parsley.makeGrammar("""
    digit = anything:x ?(x in '0123456789')
    number = <'-'{0, 1} digit+>:ds -> int(ds)
    itemlist = 
          ws item:first (ws item)*:rest -> [first] + rest
        | ws item:only -> [only]
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
    print("Tests ...")
    print(grammar('12345').number())
    print(grammar('print hello world').itemlist())
    print(grammar('print [hello world]').itemlist())
    print(grammar('print [hello [nested] world]').itemlist())
    print(grammar('line1\nline2').itemlist())
    print(grammar('to circle :radius\narc 360 :radius\nend').itemlist())
    print(grammar('print "hello').itemlist())
    print(grammar('print "hello;this is a comment\nshow [a list]').itemlist())
    print(grammar('print (2 + 3) * 5').itemlist())
    print(grammar('to equalateral :side [:colors []]').itemlist())
    print(grammar('localmake "colors (list :color :color :color)').itemlist())
    print(grammar('make "theta heading * -1 + 90').itemlist())
    #script = args.file.read()
    #print(grammar(script).itemlist())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logo programming language interpreter")
    parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        help="Logo script file to interpret.")
    args = parser.parse_args()
    main(args)
