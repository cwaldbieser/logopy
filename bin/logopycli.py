#! /usr/bin/env python

import argparse
import collections
import itertools
import numbers
import os
import string
import sys
import attr
import parsley
from logopy import errors
from logopy import procedure
from logopy import svgturtle


@attr.s
class DeferredTKTurtleEnv:

    initialized = attr.ib(default=False)
    turtle_gui = attr.ib(default=None)
    screen = attr.ib(default=None)

    @classmethod
    def create_turtle_env(cls):
        """
        Create the Deferred TK turtle environment.
        """
        return cls()

    def initialize(self, **kwargs):
        """
        Initialize the turtle environment.
        """
        global gui
        from logopy import gui
        input_handler = kwargs.get("input_handler")
        self.turtle_gui = gui.TurtleGui.make_gui(interactive=(input_handler is not None))
        self.screen = self.turtle_gui.screen
        self.screen.bgcolor("black")
        self.screen.mode("logo")
        self.screen.colormode(255)
        if input_handler is not None:
            self.turtle_gui.set_input_handler(input_handler)
        self.initialized = True

    def create_turtle(self):
        """
        Create a turtle.
        """
        turtle = gui.turtle.RawTurtle(self.screen)
        turtle.ellipse = gui.ext_ellipse.__get__(turtle)
        turtle.backend = self
        turtle.pencolor("white")
        return turtle 

    def wait_complete(self):
        """
        The main program will wait until this turtle backend
        method returns.
        For a GUI backend, this could mean the user has exited the GUI.
        """
        gui = self.turtle_gui
        gui.root.mainloop()

    @property
    def stdout(self):
        return self.turtle_gui

    @property
    def stderr(self):
        return self.turtle_gui

    @property
    def halt(self):
        return self.turtle_gui.halt

    @halt.setter
    def halt(self, value):
        self.turtle_gui.halt = value

    def process_events(self):
        """
        Process any events for the turtle backend.
        """
        self.turtle_gui.root.update_idletasks()

    def cartesian_heading(self, theta):
        """
        Return the absolute Cartesian heading for the turtle in degrees.
        """
        alpha = 90 - theta        
        alpha = alpha % 360
        return alpha

    def turtle_heading_from_cartesian_heading(self, theta):
        """
        Return an absolute turtle heading from a Cartesian heading.
        """
        alpha = 90 - theta
        alpha = alpha % 360
        return alpha

@attr.s
class LogoInterpreter:
    """
    Logo interpreter
    """
    primitives = attr.ib(default=attr.Factory(dict))
    procedures = attr.ib(default=attr.Factory(dict))
    scope_stack = attr.ib(default=attr.Factory(list))
    repcount_stack = attr.ib(default=attr.Factory(list))
    placeholder_stack = attr.ib(default=attr.Factory(list))
    grammar = attr.ib(default=None)
    script_folders = attr.ib(default=attr.Factory(list))
    turtle_backend = attr.ib(default=attr.Factory(DeferredTKTurtleEnv.create_turtle_env))
    turtle_backend_args = attr.ib(default=attr.Factory(dict))
    _screen = attr.ib(default=None)
    _turtle = attr.ib(default=None)
    debug_procs = attr.ib(default=False)
    debug_primitives = attr.ib(default=False)
    debug_tokens = attr.ib(default=False)

    @classmethod
    def create_interpreter(cls):
        interpreter = cls()
        interpreter.scope_stack.append({})
        interpreter.primitives.update(procedure.create_primitives_map())
        return interpreter

    @property
    def stdout(self):
        if self.is_turtle_active():
            return self.turtle_backend.stdout
        return sys.stdout

    @property
    def stderr(self):
        if self.is_turtle_active():
            return self.turtle_backend.stderr
        return sys.stderr

    @property
    def halt(self):
        if self.is_turtle_active():
            return self.turtle_backend.halt
        return False

    @halt.setter
    def halt(self, value):
        if self.is_turtle_active():
            self.turtle_backend.halt = value

    def is_turtle_active(self):
        return self.turtle_backend.initialized

    def process_events(self):
        if self.is_turtle_active():
            self.turtle_backend.process_events()

    def init_turtle_graphics(self):
        """
        Initialize turtle graphics.
        """
        if not self.turtle_backend.initialized:
            self.turtle_backend.initialize(**(self.turtle_backend_args))

    @property
    def turtle(self):
        """
        Initialize Turtle Graphics system if required.
        Returns the turte instance.
        """
        self.init_turtle_graphics()
        if self._turtle is None:
            self._turtle = self.turtle_backend.create_turtle()
        return self._turtle

    @property
    def screen(self):
        self.init_turtle_graphics()
        return self._screen

    def load_script(self, filename):
        """
        Attempt to load a Logo script and insert its 
        contents into the curent token stream.
        """
        script_folders = self.script_folders
        for folder in script_folders:
            pth = os.path.join(folder, filename)
            if os.path.exists(pth):
                with open(pth, "r") as f:
                    data = f.read()
                return self.process_instructionlist(data)
        raise errors.LogoError("Could not locate script `{}`.".format(filename))

    def evaluate_token_list(self, lst):
        """
        Wrap token list in TokenStream and `evaluate()`.
        """
        stream = TokenStream.make_stream(lst)
        return self.evaluate(stream)

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
        result = None
        while len(stream) > 0:
            result = self.evaluate(stream)
        return result

    def process_commands(self, tokens):
        while len(tokens) > 0:
            result = self.process_command(tokens)
            self.process_events()
        return result

    def process_command(self, tokens):
        """
        Process a command.
        """
        if self.halt:
            raise errors.HaltSignal("Received HALT")
        primitives = self.primitives
        procedures = self.procedures
        while len(tokens) > 0:
            token = tokens.popleft()  
            token = transform_qmark(token)
            is_cmd = is_command(token)
            is_spcl_frm = is_special_form(token)
            if not is_cmd and not is_spcl_frm:
                raise errors.LogoError("Expected a command.  Instead, got `{}`.".format(token))
            if is_spcl_frm:
                stream = TokenStream.make_stream(token)
                return self.process_special_form_or_expression(stream)
            else:
                command = token.lower()
                if command == 'to': 
                    procedure.process_to(self, tokens)
                elif command in primitives:
                    proc = primitives[command]
                    args = self.evaluate_args_for_command(proc.default_arity, tokens)
                    for n, arg in enumerate(args):
                        if arg is None:
                            raise errors.LogoError("Primitive `{}` received a null value for argument {}.".format(command.upper(), n+1))
                    if self.debug_primitives:
                        print("PRIMITIVE:", command, "ARGS:", args)
                    return self.execute_procedure(proc, args)
                elif command in procedures:
                    proc = procedures[command]
                    args = self.evaluate_args_for_command(proc.default_arity, tokens)
                    for n, arg in enumerate(args):
                        if arg is None:
                            raise errors.LogoError("Procedure `{}` received a null value for argument {}.".format(command.upper(), n+1))
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

    def push_placeholders(self, placeholders):
        """
        Push placeholders onto the stack.
        """
        self.placeholder_stack.append(placeholders)

    def pop_placeholders(self):
        """
        Pop placeholders off of the stack.
        """
        return self.placeholder_stack.pop()

    def get_placeholder(self, n):
        """
        Get the current placeholder at zero-based index, `n`.
        """
        return self.placeholder_stack[-1][n]

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
            return self.process_special_form_or_expression(spcl_frm_tokens)
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
            if token.startswith("-") and token != '-':
                temp_token = tokens.popleft()
                temp_token = temp_token[1:]
                tokens.appendleft(temp_token)
                return -1 * self.evaluate(tokens)
            return self.process_command(tokens)
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
        formal_params = list(itertools.chain(
            [(name, None) for name in proc.required_inputs], 
            proc.optional_inputs))
        rest_args = []
        rest_input = proc.rest_input
        for vardef, value in itertools.zip_longest(formal_params, args):
            if vardef is None:
                rest_args.append(value)
            else:
                varname, default_value = vardef
                if value is None:
                    if default_value != ':' and hasattr(default_value, 'startswith') and default_value.startswith(':'):
                        name = default_value[1:]
                        for a_scope in reversed(scope_stack):
                            if name in a_scope:
                                value = a_scope[name]
                                break
                        if value is None:
                            raise errors.LogoError("Default parameter `{}` could not find `:{}` in any scope.".format(varname, name)) 
                    else:
                        value = default_value
                if value is None:
                    raise errors.LogoError("Must have a value for formal parameter `{}` in procedure `{}`.".format(varname, proc.name))
                scope[varname] = value
        if rest_input:
            scope[rest_input] = rest_args
        result = None
        try:
            self.process_commands(tokens)
        except errors.StopSignal:
            result = None 
        except errors.OutputSignal as output:
            result = output.value
        scope_stack.pop()
        return result

    def process_special_form_or_expression(self, tokens):
        """
        Process command special form OR a parenthesized expression.
        Command token and all args will be in the token stream.
        """
        primitives = self.primitives
        procedures = self.procedures
        command_token = tokens.popleft()
        command = command_token.lower()
        second_token = None
        if len(tokens) > 0:
            second_token = tokens.peek()
        if isinstance(second_token, str) and second_token in ('-', '+', '*', '/', '=', '<>', '>=', '<='):
            tokens.appendleft(command_token)
            return self.evaluate(tokens)
        if command in primitives:
            proc = primitives[command]
        elif command in procedures:
            proc = procedures[command]
        else:
            tokens.appendleft(command_token)
            return self.evaluate(tokens)
        args = []
        while len(tokens) > 0:
            args.append(self.evaluate(tokens))
        max_arity = proc.max_arity
        if max_arity != -1 and len(args) > max_arity:
            raise errors.LogoError("There are too many arguments for `{}`.".format(command_token))
        if len(args) < proc.min_arity:
            raise errors.LogoError("Not enough arguments for `{}`.".format(command_token))
        if self.debug_primitives and command in primitives:
            print("PRIMITIVE:", command, "ARGS:", args)
        if self.debug_procs and command in procedures:
            print("PROCEDURE:", command, "ARGS:", args)
        return self.execute_procedure(proc, args)

    def receive_input(self, data):
        """
        Handles input received from GUI.
        """
        try:
            grammar = self.grammar
            tokens = parse_tokens(grammar, data, debug=self.debug_tokens)
            result = self.process_commands(tokens)
            if result is not None:
                raise errors.LogoError("You don't say what to do with `{}`.".format(result))
        except errors.HaltSignal:
            self.halt = False


@attr.s
class TokenStream:
    """
    Token stream.
    """
    tokens = attr.ib(default=None)
    processed = attr.ib(default=attr.Factory(lambda : collections.deque(list(), 10)))

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

    def appendleft(self, item):
        self.tokens.appendleft(item)

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
    float = <'-'{0, 1} digit* '.' digit+>:ds -> float(ds)
    integer = <'-'{0, 1} digit+>:ds -> int(ds)
    number = float | integer 
    itemlist = 
          ws item:first (ws item)*:rest ws -> [first] + rest
        | ws item:only ws -> [only]
    item =
          infix_rel_operator
        | expr:e (ws comment)* -> e
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
          infix_rel_operator
        | number:n (ws comment)* -> n
        | word:w (ws comment)* -> w
        | <(~' ' ~'[' ~']' anything)+>:w (ws comment)* -> w
        | (ws comment)
        | '[' ws quoted_itemlist:q ws ']' -> list(q)
        | '[' ws ']' -> []
    infix_rel_operator = '=' | '<>' | '>=' | '<='
    word = (word_char+):l -> ''.join(l)
    word_char = (escaped_char:e -> e) | (~';' unescaped_char:u -> u)
    unescaped_char = (letterOrDigit:c -> c) | (~';' punctuation:p -> p)
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
            tmp.extend(transform_tokens([item.left]))
            tmp.extend(transform_tokens([item.right]))
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

def transform_qmark(command):
    """
    If command is a `?` followed by a number, transform it to the
    special form `(?, NUMBER)`.  Otherwise, return command unaltered.
    """
    if not hasattr(command, 'startswith'):
        return command
    if not command.startswith("?"):
        return command
    try:
        pos = int(command[1:])
    except ValueError:
        return command
    return ('?', pos)

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
    interpreter = LogoInterpreter.create_interpreter()
    interpreter.turtle_backend_args = dict(input_handler=interpreter.receive_input)
    if args.turtle == 'tk':
        interpreter.init_turtle_graphics()
    interpreter.debug_tokens = args.debug_tokens
    interpreter.grammar = grammar
    interpreter.debug_primitives = args.debug_primitives
    interpreter.debug_procs = args.debug_procs
    script_folders = args.script_folder
    if script_folders is None:
        script_folders = []
    interpreter.script_folders = script_folders
    if args.turtle == 'svg':
        interpreter.turtle_backend = svgturtle.SVGTurtleEnv.create_turtle_env()
        svg_args = dict(
            output_file=args.outfile,
            html_folder=args.html,
        )
        html_args = {}
        d = vars(args)
        for k in ('html_title', 'animation_duration', 'animation_type'):
            v = d.get(k)
            if v is not None:
                html_args[k] = v
        if args.html_width:
            html_args['html_width'] = args.html_width
        if args.html_scale:
            html_args['html_scale'] = args.html_scale
        if args.animation_duration:
            html_args['animation_duration'] = args.animation_duration
        if args.animation_type:
            animation_type = args.animation_type
            if animation_type == 'onebyone':
                animation_type = 'oneByOne'
            html_args['animation_type'] = animation_type
        if args.animation_start:
            animation_start = args.animation_start
            html_args['animation_start'] = animation_start
        svg_args['html_args'] = html_args
        interpreter.turtle_backend_args = svg_args
    if args.file is not None:
        script = args.file.read()
        tokens = parse_tokens(grammar, script, debug=args.debug_tokens)
        if args.tokenize_only:
            return
        try:
            result = interpreter.process_commands(tokens)
        except Exception as ex:
            print("Processed tokens: {}".format(tokens.processed), file=sys.stderr)
            raise ex
        if result is not None:
            raise errors.LogoError("You don't say what to do with `{}`.".format(result))
    if interpreter.is_turtle_active():
        interpreter.turtle_backend.wait_complete()
    if args.debug_interpreter:
        print("")
        import pprint
        pprint.pprint(interpreter)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logo programming language interpreter")
    parser.add_argument(
        "-f",
        "--file",
        type=argparse.FileType("r"),
        help="Logo script file to interpret.")
    parser.add_argument(
        "-s",
        "--script-folder",
        action="append",
        help="Specify a folder from which the LOAD command will load Logo scripts.")
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
    parser.add_argument(
        "--tokenize-only",
        action="store_true",
        help="Only tokenize input.  Don't interpret.")
    parser.set_defaults(turtle=None)
    subparsers = parser.add_subparsers(help='Turtle back ends.')
    parser_tk = subparsers.add_parser('gui', help='GUI mode')
    parser_tk.set_defaults(turtle='tk')
    parser_tk.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Enter interactive mode.  If a Logo script is loaded, it will be run first.")
    parser_svg = subparsers.add_parser('svg', help='SVG turtle backend.')
    parser_svg.set_defaults(turtle='svg')
    parser_svg.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("w"),
        metavar="OUTFILE",
        action="store",
        help="Save turtle graphics to SVG file, OUTFILE.")
    parser_svg.add_argument(
        "--html",
        metavar="FOLDER",
        action="store",
        help="Save turtle graphics to folder, FOLDER, and create resources for web display.")
    parser_svg.add_argument(
        "--html-title",
        action="store",
        help="Set HTML title for web resources.")
    parser_svg.add_argument(
        "--html-width",
        action="store",
        type=int,
        help="Set width of image in pixels for web resources.")
    parser_svg.add_argument(
        "--html-scale",
        action="store",
        type=float,
        metavar='PERCENT',
        help="Scale width of image in web resource to PERCENT of display width.")
    parser_svg.add_argument(
        "--animation-duration",
        action="store",
        type=int,
        help="Set animation duration (in frames) for web resources.")
    parser_svg.add_argument(
        "--animation-type",
        action="store",
        choices=['sync', 'delayed', 'onebyone'],
        default='sync',
        help="Set animation type for web resources.")
    parser_svg.add_argument(
        "--animation-start",
        action="store",
        choices=['inviewport', 'automatic'],
        default='automatic',
        help="Set animation type for web resources.")
    args = parser.parse_args()
    main(args)

