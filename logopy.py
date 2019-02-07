#! /usr/bin/env python

import argparse
import string
import sys
import parsley


def main(args):
    """
    Parse Logo
    """
    grammar = parsley.makeGrammar("""
    digit = anything:x ?(x in '0123456789')
    number = <digit+>:ds -> int(ds)
    itemlist = 
          item:first (ws item)*:rest -> [first] + rest
        | item:only -> [only]
    item =
          itemlist
        | '[' ws itemlist:lst ws ']' -> lst
        | word:w (ws comment)* -> w
    word = number | <(word_char+)>:val -> val
    ascii_lower = :x ?(x in 'abcdefghijklmnopqrstuvwxyz') -> x
    ascii_upper = :x ?(x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') -> x
    ascii = ascii_lower | ascii_upper
    identifier_char = ascii | digit | '.'
    punctuation = :x ?(x in "!'#$%&\*+,-./:<=>?@^_`" '"')
    word_char = ascii | digit | punctuation
    comment = ';' rest_of_line 
    rest_of_line = <('\\\\n' | (~'\\n' anything))*>
    """, {})
    print("Tests ...")
    print(grammar('12345').number())
    print(grammar('print hello world').itemlist())
    print(grammar('print [hello world]').itemlist())
    print(grammar('print [hello [nested] world]').itemlist())
    print(grammar('line1\nline2').itemlist())
    print(grammar('to circle :radius\narc 360 :radius\nend').itemlist())
    print(grammar('print "hello').itemlist())
    print(grammar('print "hello;this is a comment\nshow [a list]').itemlist())
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
