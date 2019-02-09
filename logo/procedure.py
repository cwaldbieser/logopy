
import attr
import collections
import numbers
import random
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
    m['butfirst'] = make_primitive("butfirst", ['wordlist'], [], None, 1, process_butfirst)
    m['bf'] = m['butfirst']
    m['butfirsts'] = make_primitive("butfirsts", ['list'], [], None, 1, process_butfirsts)
    m['bfs'] = m['butfirsts']
    m['butlast'] = make_primitive("butlast", ['wordlist'], [], None, 1, process_butlast)
    m['bl'] = m['butlast']
    m['combine'] = make_primitive("combine", ['thing1', 'thing2'], [], None, 2, process_combine)
    m['dequeue'] = make_primitive("dequeue", ['queuename'], [], None, 1, process_dequeue)
    m['emptyp'] = make_primitive("emptyp", ['thing'], [], None, 1, process_emptyp)
    m['empty?'] = m['emptyp']
    m['equalp'] = make_primitive("equalp", ['thing1', 'thing2'], [], None, 2, process_equalp)
    m['equal?'] = m['equalp'] 
    m['first'] = make_primitive("first", ['thing'], [], None, 1, process_first)
    m['firsts'] = make_primitive("firsts", ['list'], [], None, 1, process_firsts)
    m['fput'] = make_primitive("fput", ['thing', 'list'], [], None, 2, process_fput)
    m['item'] = make_primitive("item", ['index', 'thing'], [], None, 2, process_item)
    m['last'] = make_primitive("last", ['thing'], [], None, 1, process_last)
    m['list'] = make_primitive("list", ['thing1', 'thing2'], [], 'others', 2, process_list)
    m['listp'] = make_primitive("listp", ['thing'], [], None, 1, process_listp)
    m['list?'] = m['listp']
    m['localmake'] = make_primitive("localmake", ['varname', 'value'], [], None, 2, process_localmake)
    m['lput'] = make_primitive("lput", ['thing', 'list'], [], None, 2, process_lput)
    m['make'] = make_primitive("make", ['varname', 'value'], [], None, 2, process_make)
    m['notequalp'] = make_primitive("notequalp", ['thing1', 'thing2'], [], None, 2, process_notequalp)
    m['notequal?'] = m['notequalp'] 
    m['pick'] = make_primitive("pick", ['list'], [], None, 1, process_pick)
    m['pop'] = make_primitive("pop", ['stackname'], [], None, 1, process_pop)
    m['print'] = make_primitive("print", ['thing'], [], 'others', 1, process_print)
    m['pr'] = m['print']
    m['push'] = make_primitive("push", ['stackname', 'thing'], [], None, 2, process_push)
    m['queue'] = make_primitive("queue", ['queuename', 'thing'], [], None, 2, process_queue)
    m['quoted'] = make_primitive("quoted", ['thing'], [], None, 1, process_quoted)
    m['remove'] = make_primitive("remove", ['thing', 'list'], [], None, 2, process_remove)
    m['remdup'] = make_primitive("remdup", ['list'], [], None, 1, process_remdup)
    m['reverse'] = make_primitive("reverse", ['list'], [], None, 1, process_reverse)
    m['sentence'] = make_primitive("sentence", ['thing1', 'thing2'], [], 'others', 2, process_sentence)
    m['se'] = m["sentence"]
    m['show'] = make_primitive("show", ['thing'], [], 'others', 1, process_show)
    m['word'] = make_primitive("word", ['word1', 'word2'], [], 'words', 2, process_word)
    m['wordp'] = make_primitive("wordp", ['thing'], [], None, 1, process_wordp)
    m['word?'] = m['wordp']
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

def process_butfirst(logo, wordlist):
    """
    The BUTFIRST command.
    """
    if len(wordlist) == 0:
        raise errors.LogoError("BUTFIRST doesn't like `{}` as input.".format(wordlist)) 
    return wordlist[1:]

def process_butfirsts(logo, lst):
    """
    The BUTFIRSTS command.
    """
    l = []
    for item in lst:
        if len(item) == 0:
            raise errors.LogoError("BUTFIRST doesn't like `{}` as input.".format(item))
        l.append(item[1:])
    return l

def process_butlast(logo, wordlist):
    """
    The BUTLAST command.
    """
    if len(wordlist) == 0:
        raise errors.LogoError("BUTLAST doesn't like `{}` as input.".format(wordlist)) 
    return wordlist[:-1]

def process_combine(logo, thing1, thing2):
    """
    The COMBINE command.
    """
    if _datatypename(thing2) in ('list'):
        return process_fput(logo, thing1, thing2)
    else:
        return process_word(logo, thing1, thing2)

def process_dequeue(logo, queuename):
    """
    The DEQUEUE command.
    """
    q = logo.get_variable_value(queuename)
    try:
        return q.pop()      
    except AttributeError:
        raise errors.LogoError("Tried to DEQUEUE from `{}`, but is not a list.".format(queuename))
    except IndexError:
        raise errors.LogoError("Tried to DEQUEUE from an empty list, `{}`.".format(queuename))

def process_emptyp(logo, thing):
    """
    The EMPTYP command.
    """
    if len(thing) == 0:
        return 'true'
    else:
        return 'false'

def process_equalp(logo, thing1, thing2):
    """
    The EQUALP command.
    """
    if thing1 == thing2:
        return 'true'
    else:
        return 'false'

def process_first(logo, thing):
    """
    The FIRST command.
    """
    if len(thing) == 0:
        raise errors.LogoError("FIRST doesn't like `{}` as input.".format(thing)) 
    else:
        return thing[0] 

def process_firsts(logo, lst):
    """
    The FIRSTS command.
    """
    l = []
    for item in lst:
        if len(item) == 0:
            raise errors.LogoError("FIRSTS doesn't like `{}` as input.".format(item))
        l.append(item[0])
    return l

def process_fput(logo, thing, lst):
    """
    The FPUT command.
    """
    l = [thing]
    l.extend(lst)
    return l

def process_item(logo, index, thing):
    """
    The ITEM command.
    """
    py_index = index - 1
    if py_index <= 0:
        raise errors.LogoError("ITEM index {} out of range.".format(index))
    try:
        return thing[py_index]
    except IndexError:
        raise errors.LogoError("ITEM index {} out of range.".format(index))

def process_last(logo, thing):
    """
    The LAST command.
    """
    if len(thing) == 0:
        raise errors.LogoError("FIRST doesn't like `{}` as input.".format(thing)) 
    else:
        return thing[-1] 

def process_list(logo, *args):
    """
    The LIST command.
    """
    return list(args)

def process_listp(logo, thing):
    """
    The LISTP command.
    """
    if _datatypename(thing) == 'list':
        return 'true'
    return 'false'

def process_localmake(logo, varname, value):
    """
    The LOCALMAKE command.
    """
    scope = logo.scope_stack[-1]
    global_scope[varname] = value

def process_lput(logo, thing, lst):
    """
    The LPUT command.
    """
    l = list(lst)
    l.append(thing)
    return l

def process_make(logo, varname, value):
    """
    The MAKE command.
    """
    global_scope = logo.scope_stack[0]
    global_scope[varname] = value 

def process_notequalp(logo, thing1, thing2):
    """
    The NOTEQUALP command.
    """
    if thing1 != thing2:
        return 'true'
    else:
        return 'false'

def process_pick(logo, lst):
    """
    The PICK command.
    """
    if len(lst) == 0:
        raise errors.LogoError("PICK does not like `{}` as input.".format(lst))
    return random.choice(lst)

def process_pop(logo, stackname):
    """
    The POP command.
    """
    stack = logo.get_variable_value(stackname)
    try:
        return stack.pop(0)      
    except AttributeError:
        raise errors.LogoError("Tried to POP from `{}`, but it is not a list.".format(stackname))
    except IndexError:
        raise errors.LogoError("Tried to POP from empty stack, `{}`.".format(stackname))

def process_print(logo, *args):
    """
    The PRINT command.
    """
    reps = []
    for arg in args:
        if _datatypename(arg) == 'list':
            reps.append(_list_contents_repr(arg, include_braces=False))
        elif _datatypename(arg) == 'word':
            reps.append(str(arg))
    print(' '.join(reps))

def process_push(logo, stackname, thing):
    """
    The PUSH command.
    """
    stack = logo.get_variable_value(stackname)
    try:
        stack.insert(0, thing)      
    except AttributeError:
        raise errors.LogoError("Tried to PUSH to `{}`, but is not a list.".format(stackname))

def process_queue(logo, queuename, thing):
    """
    The QUEUE command.
    """
    q = logo.get_variable_value(queuename)
    try:
        q.insert(0, thing)      
    except AttributeError:
        raise errors.LogoError("Tried to QUEUE to `{}`, but it is not a list.".format(queuename))

def process_quoted(logo, thing):
    """
    The QUOTED command.
    """
    if _datatypename(thing) != 'word':
        return thing
    return '"{}'.format(thing)

def process_remove(logo, thing, lst):
    """
    The REMOVE command.
    """
    if _datatypename(lst) == 'list':
        return [x for x in lst if x != thing]
    elif _datatypename(lst) == 'word':
        return lst.replace(thing, "")
    else:
        raise errors.LogoError("REMOVE cannot be used on a {}.".format(_datatypename(lst)))

def process_remdup(logo, lst):
    """
    The REMDUP command.
    """
    l = collections.deque([])
    s = set([])
    for x in reversed(lst):
        if not x in s:
            l.appendleft(x)
            s.add(x)
    dtype = _datatypename(lst)
    if dtype == 'list':
        return list(l)
    elif dtype == 'word':
        return ''.join(l)
    else:
        raise errors.LogoError("REMDUP cannot be used on a {}.".format(dtype))

def process_reverse(logo, lst):
    """
    The REVERSE command.
    """
    r = list(lst)
    r.reverse()
    return r

def process_sentence(logo, *args):
    """
    The SENTENCE command.
    """
    sentence = []
    for item in args:
        dtype = _datatypename(item)
        if dtype == 'list':
            for subitem in item:
                sentence.append(subitem)
        elif dtype == 'word':
            sentence.append(item)
        else:
            raise errors.LogoError("SENTENCE cannot be used on a {}.".format(dtype))
    return sentence

def process_word(logo, *args):
    """
    The WORD command.
    """
    for arg in args:
        dtype = _datatypename(arg)
        if dtype != 'word':
            raise errors.LogoError("Expected a word, but got a {} instead.".format(dtype))
    return ''.join(args)

def process_wordp(logo, thing):
    """
    The WORDP command.
    """
    dtype = _datatypename(thing)
    if dtype == 'word':
        return 'true'
    return 'false'

def _datatypename(o):
    """
    Returns a sting corresponding to the Logo data type name.
    """
    if isinstance(o, str) or isinstance(o, numbers.Number):
        return 'word'
    if isinstance(o, list):
        return 'list'
    return 'unknown'

def _list_contents_repr(o, include_braces=True):
    dtype = _datatypename(o)
    if dtype == 'list':
        rep = ' '.join([_list_contents_repr(x) for x in o])
        if include_braces:
            rep = "[{}]".format(rep)
        return rep
    elif dtype == 'word':
        return str(o)
    else:
        raise errors.LogoError("Unknown data type for `{}`.".format(o))

def process_show(logo, *args):
    """
    The SHOW command.
    """
    reps = []
    for arg in args:
        dtype = _datatypename(arg)
        if dtype == 'list':
            reps.append(_list_contents_repr(arg))
        elif dtype == 'word':
            reps.append(str(arg))
        else:
            raise errors.LogoError("SHOW doesn't know how to show type {}.".format(dtype))
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
            if _datatypename(peek) == 'list' and len(peek) > 1:
                opt_name = peek[0]
                if _is_dots_name(opt_name):
                    optional_inputs.append((opt_name[1:], tokens.popleft()[1:]))
                    continue
        break
    rest_input = None
    if len(tokens) > 0:
        peek = tokens[0]
        if _datatypename(peek) == 'list' and len(peek) == 1:
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

