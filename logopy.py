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
        | word
    word = number | <(word_char+)>:val -> val
    ascii_lower = :x ?(x in 'abcdefghijklmnopqrstuvwxyz') -> x
    ascii_upper = :x ?(x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') -> x
    ascii = ascii_lower | ascii_upper
    identifier_char = ascii | digit | '.'
    punctuation = :x ?(x in "!'#$%&\*+,-./:;<=>?@^_`")
    word_char = ascii | digit | punctuation
    """, {})
    print(grammar('12345').number())
    print(grammar('print hello world').itemlist())
    print(grammar('print [hello world]').itemlist())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logo programming language interpreter")
#    parser.add_argument(
#        "file",
#        type=argparse.FileType("r"),
#        help="Logo script file to interpret.")
    args = parser.parse_args()
    main(args)
