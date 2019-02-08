
import attr
import collections
from logo import errors


@attr.s
class LogoProcedure:
    """
    Logo procedure.
    """
    name = attr.ib(default=None)
    required_inputs = attr.ib(default=attr.Factory(list))
    optional_inputs = attr.ib(default=attr.Factory(list))
    rest_input = attr.ib(default=None)
    default_arity = attr.ib(default=None)
    tokens = attr.ib(default=None)
    primitive_func = attr.ib(default=None)
   
    @classmethod 
    def make_procedure(cls, name, required_inputs, optional_inputs, rest_input, default_arity, tokens):
        p = cls()
        p.name = name
        p.required_inputs = required_inputs
        p.optional_inputs = optional_inputs
        p.rest_input = rest_input
        p.default_arity = default_arity
        p.tokens = tokens
        return p

    @classmethod
    def make_primitive(cls, name, required_inputs, optional_inputs, rest_input, default_arity, func):
        p = cls()
        p.name = name
        p.default_arity = default_arity
        p.required_inputs = required_inputs
        p.optional_inputs = optional_inputs
        p.rest_input = rest_input
        p.default_arity = default_arity
        p.primitive_func = func
        return p

    @property
    def max_arity(self):
        """
        Return the maximum arity for the proc.
        Return -1 for unlimited arity.
        """
        if self.rest_input:
            return -1
        return len(self.required_inputs) + len(self.optional_inputs)

    @property
    def min_arity(self):
        """
        Return the minimum arity for the proc.
        """
        return len(self.required_inputs)


def create_primitives_map():
    """
    Create a mapping of primitives names to procedure information.
    """
    m = {}
    make_primitive = LogoProcedure.make_primitive
    m['fput'] = make_primitive("fput", ['thing', 'list'], [], None, 2, process_fput)
    m['list'] = make_primitive("list", ['thing1', 'thing2'], [], 'others', 2, process_list)
    m['localmake'] = make_primitive("localmake", ['varname', 'value'], [], None, 2, process_localmake)
    m['lput'] = make_primitive("lput", ['thing', 'list'], [], None, 2, process_lput)
    m['make'] = make_primitive("make", ['varname', 'value'], [], None, 2, process_make)
    m['print'] = make_primitive("print", ['thing'], [], 'others', 1, process_print)
    m['pr'] = m['print']
    m['sentence'] = make_primitive("sentence", ['thing1', 'thing2'], [], 'others', 2, process_sentence)
    m['se'] = m["sentence"]
    m['show'] = make_primitive("show", ['thing'], [], 'others', 1, process_show)
    m['word'] = make_primitive("word", ['word1', 'word2'], [], 'words', 2, process_word)
    return m
    
def _is_dots_name(token):
    """
    Is the token a formal parameter or a reference to some value?
    """
    if not hasattr(token, 'startswith'):
        return False
    if not token.startswith(":"):
        return False
    if not len(token) > 1:
        return False
    return True

def process_fput(logo, thing, lst):
    """
    The FPUT command.
    """
    l = [thing]
    l.extend(lst)
    return l

def process_lput(logo, thing, lst):
    """
    The LPUT command.
    """
    l = list(lst)
    l.append(thing)
    return l

def process_word(logo, *args):
    """
    The WORD command.
    """
    return ''.join(args)

def process_list(logo, *args):
    """
    The LIST command.
    """
    return list(args)

def process_sentence(logo, *args):
    """
    The SENTENCE command.
    """
    sentence = []
    for item in args:
        if isinstance(item, list):
            for subitem in item:
                sentence.append(subitem)
        else:
            sentence.append(item)
    return sentence

def process_make(logo, varname, value):
    """
    The MAKE command.
    """
    global_scope = logo.scope_stack[0]
    global_scope[varname] = value 

def process_localmake(logo, varname, value):
    """
    The LOCALMAKE command.
    """
    scope = logo.scope_stack[-1]
    global_scope[varname] = value

def process_print(logo, *args):
    """
    The PRINT command.
    """
    reps = []
    for arg in args:
        if isinstance(arg, list):
            reps.append(_list_contents_repr(arg, include_braces=False))
        else:
            reps.append(str(arg))
    print(' '.join(reps))

def _list_contents_repr(o, include_braces=True):
    if isinstance(o, list):
        rep = ' '.join([_list_contents_repr(x) for x in o])
        if include_braces:
            rep = "[{}]".format(rep)
        return rep
    return str(o)

def process_show(logo, *args):
    """
    The SHOW command.
    """
    reps = []
    for arg in args:
        if isinstance(arg, list):
            reps.append(_list_contents_repr(arg))
        else:
            reps.append(str(arg))
    print(' '.join(reps))

def process_to(logo, tokens):
    """
    Process the TO command.
    """
    try:
        procedure_name = tokens.popleft()
    except IndexError:
        raise errors.LogoError("TO command requires a procedure name.")
    required_inputs = []
    while True:
        if len(tokens) > 0:
            peek = tokens[0]
            if _is_dots_name(peek):
                required_inputs.append(tokens.popleft()[1:])
                continue
        break
    optional_inputs = []
    while True:
        if len(tokens) > 0:
            peek = tokens[0]
            if isinstance(peek, list) and len(peek) > 1:
                opt_name = peek[0]
                if _is_dots_name(opt_name):
                    optional_inputs.append((opt_name[1:], tokens.popleft()[1:]))
                    continue
        break
    rest_input = None
    if len(tokens) > 0:
        peek = tokens[0]
        if isinstance(peek, list) and len(peek) ==1:
            rest_name = peek[0]
            if _is_dots_name(rest_name):
                rest_input = tokens.popleft()[1:]
    default_arity = len(required_inputs)
    if len(tokens) > 0:
        peek = tokens[0]
        if isinstance(peek, int):
            default_arity = tokens.popleft()
    procedure_tokens = collections.deque([])
    try:
        token = tokens.popleft()
    except IndexError:
        raise errors.LogoError("Expected END to complete procedure `{}`.".format(procedure_name))
    _test = (lambda x: hasattr(x, 'lower') and x.lower() == 'end')
    while not _test(token):
        procedure_tokens.append(token)
        try:
            token = tokens.popleft()
        except IndexError:
            raise errors.LogoError("Expected END to complete procedure `{}`.".format(procedure_name))
    procedure = LogoProcedure.make_procedure(
        name=procedure_name,
        required_inputs=required_inputs,
        optional_inputs=optional_inputs,
        rest_input=rest_input,
        default_arity=default_arity,
        tokens=procedure_tokens)
    logo.procedures[procedure_name.lower()] = procedure 

