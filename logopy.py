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
    repcount_stack = attr.ib(default=attr.Factory(list))
    grammar = attr.ib(default=None)
    debug_procs = attr.ib(default=False)
    debug_primitives = attr.ib(default=False)
    debug_tokens = attr.ib(default=False)

    @classmethod
    def create_interpreter(cls):
        interpreter = cls()
        interpreter.scope_stack.append({})
        interpreter.primitives.update(procedure.create_primitives_map())
        return interpreter

    def evaluate_readlist(self, data):
        """
        Evaluate input as READLIST.
        """
        stream = TokenStream.make_stream(self.grammar(data).itemlist())
        return self.evaluate(stream) 

    def process_instructionlist(self, script):
        """
        Process a script, which should represent a list of instructions
        when tokenized.
        """
        stream = parse_tokens(self.grammar, script, debug=self.debug_tokens)
        return self.process_commands(stream)

    def process_commands(self, tokens):
        while len(tokens) > 0:
            result = self.process_command(tokens)
        return result

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
                else:
                    raise errors.LogoError("I don't know how to `{}`.".format(token))

    def get_variable_value(self, varname):
        """
        Get the value of the named variable from the dynamic scope.
        """
        scopes = self.scope_stack
        for scope in reversed(scopes):
            if varname in scope:
                value = scope[varname]
                if value is None:
                    raise errors.LogoError("`{}` has no value.".format(varname))
                return value
        raise errors.LogoError("No scope has a variable named `{}`.".format(varname))

    def get_repcount(self):
        """
        Get the current REPCOUNT count.
        Returns -1 on no REPEAT or FOREVER.
        """
        rep_scopes = self.repcount_stack
        if len(rep_scopes) == 0:
            return -1
        return rep_scopes[-1]

    def set_repcount(self, n):
        """
        Sets the current repcount.
        """
        self.repcount_stack[-1] = n

    def create_repcount_scope(self):
        """
        Create a new repcount scope.
        """
        self.repcount_stack.append(-1)

    def destroy_repcount_scope(self):
        """
        Destroy a repcount scope.
        """
        self.repcount_stack.pop()

    def evaluate(self, tokens):
        """
        Evaluate and check for infix.
        """
        value = self.evaluate_value(tokens)
        if isinstance(value, numbers.Number):
            terms = [value]
            while True:
                peek = tokens.peek()
                if peek == '-':
                    tokens.popleft()
                    terms.append(-self.evaluate_value(tokens))
                elif peek == '+':
                    tokens.popleft()
                    terms.append(self.evaluate_value(tokens))
                elif peek == '*':
                    tokens.popleft()
                    terms[-1] *= self.evaluate_value(tokens)
                elif peek == '/':
                    tokens.popleft()
                    terms[-1] /= self.evaluate_value(tokens)
                elif peek == '<':
                    tokens.popleft()
                    p = self.primitives['lessp'].primitive_func
                    return p(self, sum(terms), self.evaluate_value(tokens))
                elif peek == '<=':
                    tokens.popleft()
                    p = self.primitives['lessequalp'].primitive_func
                    return p(self, sum(terms), self.evaluate_value(tokens))
                elif peek == '>':
                    tokens.popleft()
                    p = self.primitives['greaterp'].primitive_func
                    return p(self, sum(terms), self.evaluate_value(tokens))
                elif peek == '>=':
                    tokens.popleft()
                    p = self.primitives['greaterequalp'].primitive_func
                    return p(self, sum(terms), self.evaluate_value(tokens))
                elif peek == '=':
                    tokens.popleft()
                    p = self.primitives['equalp'].primitive_func
                    return p(self, sum(terms), self.evaluate_value(tokens))
                elif peek == '<>':
                    tokens.popleft()
                    p = self.primitives['notequalp'].primitive_func
                    return p(self, sum(terms), self.evaluate_value(tokens))
                else:
                    break
            return sum(terms)
        else:
            peek = tokens.peek()
            if peek == '=':
                tokens.popleft()
                p = self.primitives['equalp'].primitive_func
                return p(self, value, self.evaluate_value(tokens))
            elif peek == '<>':
                tokens.popleft()
                p = self.primitives['notequalp'].primitive_func
                return p(self, value, self.evaluate_value(tokens))
            else:
                return value

    def evaluate_value(self, tokens, quoted=False):
        """
        Evaluate the next value from the token stream.
        """
        token = tokens.peek()
        if token is None:
            raise errors.LogoError("Expected a value but instead got EOF.")
        if is_list(token):
            lst_tokens = TokenStream.make_stream(tokens.popleft())
            return self.evaluate_list(lst_tokens)
        if is_special_form(token):
            spcl_frm_tokens = TokenStream.make_stream(tokens.popleft())
            return self.process_special_form(spcl_frm_tokens)
        if is_paren_expr(token):
            expr_tokens = TokenStream.make_stream(tokens.popleft())
            return self.evaluate(expr_tokens)
        if isinstance(token, numbers.Number):
            num = tokens.popleft()
            return num
        if not quoted:
            if token.startswith('"'):
                return tokens.popleft()[1:]
            if token.startswith(':'):
                return self.get_variable_value(tokens.popleft()[1:])
            if token == '#':
                tokens.popleft()
                return self.get_repcount()
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
            args.append(self.evaluate(tokens))
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
            raise errors.LogoError("I don't know how to `{}`.".format(command_token)) 
        args = []
        while len(tokens) > 0:
            args.append(self.evaluate(tokens))
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


@attr.s
class DelayedValue:
    op = attr.ib(default=None)
    left = attr.ib(default=None)
    right = attr.ib(default=None)


@attr.s
class Comment:
    text = attr.ib()


def calculate(start, pairs):
    result = start
    for op, value in pairs:
        immediate_value = False
        if isinstance(result, numbers.Number) and isinstance(value, numbers.Number):
            immediate_value = True
        if op == '+':
            if immediate_value:
                result += value
            else:
                result = DelayedValue('sum', result, value)
        elif op == '-':
            if immediate_value:
                result -= value
            else:
                result = DelayedValue('difference', result, value)
        elif op == '*':
            if immediate_value:
                result *= value
            else:
                result = DelayedValue('product', result, value)
        elif op == '/':
            if immediate_value:
                result /= value
            else:
                result = DelayedValue('quotient', result, value)
    return result

def make_token_grammar():
    """
    Make the token grammar.
    """
    grammar = parsley.makeGrammar(r"""
    punctuation = :x ?(x in "+-*/!'#$%&\,.:<=>?@^_`;" '"') -> x
    digits = <digit+>
    float = ('-'{0, 1} digits? '.' digits):ds -> float(ds)
    int = ('-'{0, 1} digits):ds -> int(ds)
    number = float | int 
    ascii_lower = :x ?(x in 'abcdefghijklmnopqrstuvwxyz') -> x
    ascii_upper = :x ?(x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') -> x
    ascii = ascii_lower | ascii_upper
    itemlist = 
          ws item:first (ws item)*:rest ws -> [first] + rest
        | ws item:only ws -> [only]
    item =
          expr:e (ws comment)* -> e
        | word:w (ws comment)* -> w
        | itemlist
        | '[' ws quoted_itemlist:q ws ']' -> list(q)
        | '[' ws ']' -> []
        | '(' itemlist:lst ')' -> tuple(lst) 
        | (ws comment)
    quoted_itemlist = 
          ws quoted_item:first (ws quoted_item)*:rest ws -> [first] + rest
        | ws quoted_item:only ws -> [only]
    quoted_item =
          word:qw (ws comment)* -> qw
        | <(~' ' ~'[' ~']' anything)+>:w (ws comment)* -> w
        | (ws comment)
        | '[' ws quoted_itemlist:q ws ']' -> list(q)
        | '[' ws ']' -> []
    word = (word_char+):l -> ''.join(l)
    word_char = (escaped_char:e -> e) | (~';' unescaped_char:u -> u)
    unescaped_char = (ascii:a -> a) | (digit:d -> d) | (~';' punctuation:p -> p)
    escaped_char = '\\' (anything:c -> c)
    comment = <';' rest_of_line>:c -> Comment(c)  
    rest_of_line = <('\\n' | (~'\n' anything))*>
    parens = '(' ws expr:e ws ')' -> e
    value = (number:n ->n) | (parens:p -> p)
    factor = (value:v -> v) | (word:w -> w)
    add = '+' ws expr2:n -> ('+', n)
    mul = '*' ws factor:n -> ('*', n)
    div = '/' ws factor:n -> ('/', n)
    addonly = ws add
    muldiv = ws (mul | div)
    expr = expr2:left addonly*:right -> calculate(left, right)
    expr2 = factor:left muldiv*:right -> calculate(left, right)
    """, {"calculate": calculate, "Comment": Comment})
    
    return grammar

def transform_tokens(tokens):
    """
    Transform the shape of the tokens.
    """
    tmp = []
    for item in tokens:
        if isinstance(item, DelayedValue):
            tmp.append(item.op)
            tmp.append(item.left)
            tmp.append(item.right)
        elif isinstance(item, Comment):
            continue
        elif is_list(item):
            tmp.append(transform_tokens(item))
        elif isinstance(item, tuple):
            tmp.append(tuple(transform_tokens(item)))
        else:
            tmp.append(item)
    return tmp 

def parse_tokens(grammar, script, debug=False):
    """
    Parse a Logo script.
    Return a list of tokens.
    """
    token_lst = grammar(script).itemlist()
    token_lst = transform_tokens(token_lst)
    tokens = TokenStream.make_stream(token_lst)
    if debug:
        print("PARSED TOKENS:", tokens)
    return tokens

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

def is_special_form(token):
    if not isinstance(token, tuple):
        return False
    first = token[0]
    if is_command(first):
        return True
    return False

def is_paren_expr(token):
    if not isinstance(token, tuple):
        return False
    first = token[0]
    if is_command(first):
        return False
    return True
        
def is_command(token):
    if not isinstance(token, str):
        return False
    if token.startswith(":"):
        return False
    if token.startswith('"'):
        return False
    return True

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
    tokens = parse_tokens(grammar, script, debug=args.debug_tokens)
    interpreter = LogoInterpreter.create_interpreter()
    interpreter.debug_tokens = args.debug_tokens
    interpreter.grammar = grammar
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

