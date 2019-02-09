#! /usr/bin/env python

import argparse
import collections
import itertools
import numbers
import string
import sys
import attr
import parsley
from logo import errors
from logo import procedure


@attr.s
class LogoInterpreter:
    """
    Logo interpreter
    """
    primitives = attr.ib(default=attr.Factory(dict))
    procedures = attr.ib(default=attr.Factory(dict))
    scope_stack = attr.ib(default=attr.Factory(list))
    debug_procs = attr.ib(default=False)
    debug_primitives = attr.ib(default=False)

    @classmethod
    def create_interpreter(cls):
        interpreter = cls()
        interpreter.scope_stack.append({})
        interpreter.primitives.update(procedure.create_primitives_map())
        return interpreter

    def process_commands(self, tokens):
        while len(tokens) > 0:
            self.process_command(tokens)

    def process_command(self, tokens):
        """
        Process a command.
        """
        primitives = self.primitives
        procedures = self.procedures
        while len(tokens) > 0:
            token = tokens.popleft()  
            is_cmd = is_command(token)
            is_spcl_frm = is_special_form(token)
            if not is_cmd and not is_spcl_frm:
                raise errors.LogoError("Expected a command.  Instead, got `{}`.".format(token))
            if is_spcl_frm:
                stream = TokenStream.make_stream(token)
                self.process_special_form(stream)
            else:
                command = token.lower()
                if command == 'to': 
                    procedure.process_to(self, tokens)
                elif command in primitives:
                    proc = primitives[command]
                    args = self.evaluate_args_for_command(proc.default_arity, tokens)
                    if self.debug_primitives:
                        print("PRIMITIVE:", command, "ARGS:", args)
                    return self.execute_procedure(proc, args)
                elif command in procedures:
                    proc = procedures[command]
                    args = self.evaluate_args_for_command(proc.default_arity, tokens)
                    if self.debug_procs:
                        print("PROCEDURE:", command, "ARGS:", args)
                    return self.execute_procedure(proc, args)

    def get_variable_value(self, varname):
        """
        Get the value of the named variable from the dynamic scope.
        """
        scopes = self.scope_stack
        for scope in reversed(scopes):
            if varname in scope:
                return scope[varname]
        raise errors.LogoError("No scope has a variable named `{}`.".format(varname))

    def evaluate_value(self, tokens, quoted=False):
        """
        Evaluate the next value from the token stream.
        """
        token = tokens.peek()
        if token is None:
            raise LogoError("Expected a value but instead got EOF.")
        if is_list(token):
            lst_tokens = TokenStream.make_stream(tokens.popleft())
            return self.evaluate_list(lst_tokens)
        if is_special_form(token):
            spcl_frm_tokens = TokenStream.make_stream(tokens.popleft())
            return self.process_special_form(spcl_frm_tokens)
        if isinstance(token, numbers.Number):
            return tokens.popleft()
        if not quoted:
            if token.startswith('"'):
                return tokens.popleft()[1:]
            if token.startswith(':'):
                return self.get_variable_value(tokens.popleft()[1:])
            if token in self.primitives or token in self.procedures:
                return self.process_command(tokens)
            else:
                raise errors.LogoError("I don't know how to `{}`.".format(token))
        else:
            return tokens.popleft()

    def evaluate_list(self, tokens):
        """
        Evaluate list elements.
        """
        lst = []
        while len(tokens) > 0:
            value = self.evaluate_value(tokens, quoted=True)
            lst.append(value)
        return lst

    def evaluate_args_for_command(self, arity, tokens):
        """
        Evaluate tokens to provide `arity` arguments for a command.
        """
        args = []
        while len(args) < arity:
            args.append(self.evaluate_value(tokens))
        return args

    def execute_procedure(self, proc, args):
        """
        Execute a procedure with args, `args`.
        """
        if proc.primitive_func:
            return proc.primitive_func(self, *args)
        tokens = TokenStream.make_stream(proc.tokens)
        scope = {}
        scope_stack = self.scope_stack
        scope_stack.append(scope) 
        formal_params = itertools.chain(proc.required_inputs, proc.optional_inputs)
        rest_args = []
        rest_input = proc.rest_input
        for varname, value in itertools.zip_longest(formal_params, args):
            if args is None:
                break
            if varname is None:
                rest_args.append(value)
            else:
                scope[varname] = value
        if rest_input:
            scope[rest_input] = rest_args
        self.process_commands(tokens)
        scope_stack.pop()

    def process_special_form(self, tokens):
        """
        Process command special form.
        Command token and all args will be in the token stream.
        """
        primitives = self.primitives
        procedures = self.procedures
        command_token = tokens.popleft()
        command = command_token.lower()
        if command in primitives:
            proc = primitives[command]
        elif command in procedures:
            proc = procedures[command]
        else:
            raise LogoError("I don't know how to `{}`.".format(command_token)) 
        args = []
        while len(tokens) > 0:
            args.append(self.evaluate_value(tokens))
        max_arity = proc.max_arity
        if max_arity != -1 and len(args) > max_arity:
            raise errors.LogoError("There are too many arguments for `{}`.".format(command_token))
        if len(args) < proc.min_arity:
            raise errors.LogoError("Not enough arguments for `{}`.".format(command_token))
        return self.execute_procedure(proc, args)

@attr.s
class TokenStream:
    """
    Token stream.
    """
    tokens = attr.ib(default=None)
    processed = attr.ib(default=attr.Factory(list))

    @classmethod
    def make_stream(cls, lst):
        stream = cls()
        stream.tokens = collections.deque(lst)
        return stream

    def __getitem__(self, key):
        return self.tokens[key]

    def popleft(self):
        token = self.tokens.popleft()
        self.processed.append(token)
        return token

    def append(self, item):
        self.tokens.append(item)

    def __len__(self):
        return len(self.tokens)

    def peek(self):
        tokens = self.tokens
        if len(tokens) > 0:
            return tokens[0]
        else:
            return None


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
    digits = <digit*>
    digit1_9 = :x ?(x in '123456789')
    float = <'-'{0, 1} digit1_9 digit* '.' digit+>:ds -> float(ds)
    int = <'-'{0, 1} digit1_9 digit*>:ds -> int(ds)
    number = float | int
    itemlist = 
          ws item:first (ws item)*:rest ws -> [first] + rest
        | ws item:only ws -> [only]
    item =
          itemlist
        | '[' ws itemlist:lst ws ']' -> lst
        | '[' ws ']' -> []
        | word:w (ws comment)* -> w
        | '(' itemlist:lst ')' -> tuple(lst) 
        | (ws comment)
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
    return TokenStream.make_stream(grammar(script).itemlist())

def run_tests(grammar):
    """
    Run the tests.
    """
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

def is_command(token):
    return hasattr(token, "lower")

def is_special_form(token):
    return isinstance(token, tuple)

def is_list(token):
    return isinstance(token, list)

def main(args):
    """
    Parse Logo
    """
    grammar = make_token_grammar()
    if args.tests:
        run_tests(grammar)
    script = args.file.read()
    tokens = parse_tokens(grammar, script)
    if args.debug_tokens:
        print("PARSED TOKENS:", tokens)
    interpreter = LogoInterpreter.create_interpreter()
    if args.debug_procs:
        interpreter.debug_procs = True
    try:
        interpreter.process_commands(tokens)
    except Exception as ex:
        print("Processed tokens: {}".format(tokens.processed), file=sys.stderr)
        raise ex
    if args.debug_interpreter:
        print("")
        print(interpreter)

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
    parser.add_argument(
        "--debug-procs",
        action="store_true",
        help="Debug procedures.")
    parser.add_argument(
        "--debug-primitives",
        action="store_true",
        help="Debug procedures.")
    parser.add_argument(
        "--debug-tokens",
        action="store_true",
        help="Debug parsed tokens.")
    parser.add_argument(
        "--debug-interpreter",
        action="store_true",
        help="Dump interpreter state after script completes.")
    args = parser.parse_args()
    main(args)

