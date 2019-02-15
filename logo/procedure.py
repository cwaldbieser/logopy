
import attr
import collections
import functools
import math
import numbers
import operator
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
    m['.eq'] = make_primitive(".eq", ['thing1', 'thing2'], [], None, 2, process_dot_eq)
    m['and'] = make_primitive("and", ['tf1', 'tf2'], [], 'tfs', 2, process_and)
    m['arctan'] = make_primitive("arctan", ['x'], ['y'], None, 1, process_arctan)
    m['beforep'] = make_primitive("beforep", ['word1', 'word2'], [], None, 2, process_beforep)
    m['before?'] = m['beforep']
    m['butfirst'] = make_primitive("butfirst", ['wordlist'], [], None, 1, process_butfirst)
    m['bf'] = m['butfirst']
    m['butfirsts'] = make_primitive("butfirsts", ['list'], [], None, 1, process_butfirsts)
    m['bfs'] = m['butfirsts']
    m['butlast'] = make_primitive("butlast", ['wordlist'], [], None, 1, process_butlast)
    m['bl'] = m['butlast']
    m['char'] = make_primitive("char", ['int'], [], None, 1, process_char)
    m['combine'] = make_primitive("combine", ['thing1', 'thing2'], [], None, 2, process_combine)
    m['count'] = make_primitive("count", ['thing'], [], None, 1, process_count)
    m['cos'] = make_primitive("cos", ['degrees'], [], None, 1, process_cos)
    m['dequeue'] = make_primitive("dequeue", ['queuename'], [], None, 1, process_dequeue)
    m['difference'] = make_primitive("difference", ['num1', 'num2'], [], None, 2, process_difference)
    m['do.while'] = make_primitive("do.while", ['instrlist', 'tfexpr'], [], None, 2, process_dowhile)
    m['emptyp'] = make_primitive("emptyp", ['thing'], [], None, 1, process_emptyp)
    m['empty?'] = m['emptyp']
    m['equalp'] = make_primitive("equalp", ['thing1', 'thing2'], [], None, 2, process_equalp)
    m['equal?'] = m['equalp'] 
    m['exp'] = make_primitive("exp", ['num'], [], None, 1, process_exp)
    m['first'] = make_primitive("first", ['thing'], [], None, 1, process_first)
    m['firsts'] = make_primitive("firsts", ['list'], [], None, 1, process_firsts)
    m['for'] = make_primitive("for", ['forcontrol', 'instrlist'], [], None, 2, process_for)
    m['fput'] = make_primitive("fput", ['thing', 'list'], [], None, 2, process_fput)
    m['greaterequalp'] = make_primitive("greaterequalp", ['num1', 'num2'], [], None, 2, process_greaterequalp)
    m['greaterequal?'] = m['greaterequalp']
    m['greaterp'] = make_primitive("greaterp", ['num1', 'num2'], [], None, 2, process_greaterp)
    m['greater?'] = m['greaterp']
    m['if'] = make_primitive("if", ['tf', 'instructionlist'], ['instructionlist2'], None, 2, process_if)
    m['ifelse'] = make_primitive("ifelse", ['tf', 'instrlist1', 'instrlist2'], [], None, 3, process_ifelse)
    m['ignore'] = make_primitive("ignore", ['value'], [], None, 1, process_ignore)
    m['int'] = make_primitive("int", ['num'], [], None, 1, process_int)
    m['iseq'] = make_primitive("iseq", ['from', 'to'], [], None, 2, process_iseq)
    m['item'] = make_primitive("item", ['index', 'thing'], [], None, 2, process_item)
    m['last'] = make_primitive("last", ['thing'], [], None, 1, process_last)
    m['lessequalp'] = make_primitive("lessequalp", ['num1', 'num2'], [], None, 2, process_lessequalp)
    m['lessequal?'] = m['lessequalp']
    m['lessp'] = make_primitive("lessp", ['num1', 'num2'], [], None, 2, process_lessp)
    m['less?'] = m['lessp']
    m['list'] = make_primitive("list", ['thing1', 'thing2'], [], 'others', 2, process_list)
    m['listp'] = make_primitive("listp", ['thing'], [], None, 1, process_listp)
    m['list?'] = m['listp']
    m['local'] = make_primitive("local", ['varname'], [], 'varnames', 1, process_local)
    m['localmake'] = make_primitive("localmake", ['varname', 'value'], [], None, 2, process_localmake)
    m['lput'] = make_primitive("lput", ['thing', 'list'], [], None, 2, process_lput)
    m['log10'] = make_primitive("log10", ['num'], [], None, 1, process_log10)
    m['lowercase'] = make_primitive("lowercase", ['word'], [], None, 1, process_lowercase)
    m['ln'] = make_primitive("ln", ['num'], [], None, 1, process_ln)
    m['make'] = make_primitive("make", ['varname', 'value'], [], None, 2, process_make)
    m['member'] = make_primitive("member", ['thing1', 'thing2'], [], None, 2, process_member)
    m['memberp'] = make_primitive("memberp", ['thing1', 'thing2'], [], None, 2, process_memberp)
    m['member?'] = m['memberp']
    m['modulo'] = make_primitive("modulo", ['num1', 'num2'], [], None, 2, process_modulo)
    m['not'] = make_primitive("not", ['tf'], [], None, 1, process_not)
    m['notequalp'] = make_primitive("notequalp", ['thing1', 'thing2'], [], None, 2, process_notequalp)
    m['notequal?'] = m['notequalp'] 
    m['numberp'] = make_primitive("numberp", ['thing'], [], None, 1, process_numberp)
    m['number?'] = m['numberp']
    m['or'] = make_primitive("or", ['tf1', 'tf2'], [], 'tfs', 2, process_or)
    m['output'] = make_primitive("output", ['value'], [], None, 1, process_output)
    m['op'] = m['output']
    m['pick'] = make_primitive("pick", ['list'], [], None, 1, process_pick)
    m['pop'] = make_primitive("pop", ['stackname'], [], None, 1, process_pop)
    m['power'] = make_primitive("power", ['num1', 'num2'], [], None, 2, process_power)
    m['print'] = make_primitive("print", ['thing'], [], 'others', 1, process_print)
    m['pr'] = m['print']
    m['product'] = make_primitive("product", ['num1', 'num2'], [], 'nums', 2, process_product)
    m['push'] = make_primitive("push", ['stackname', 'thing'], [], None, 2, process_push)
    m['queue'] = make_primitive("queue", ['queuename', 'thing'], [], None, 2, process_queue)
    m['quoted'] = make_primitive("quoted", ['thing'], [], None, 1, process_quoted)
    m['quotient'] = make_primitive("quotient", ['num1', 'num2'], [], None, 2, process_quotient)
    m['radarctan'] = make_primitive("radarctan", ['x'], ['y'], None, 1, process_radarctan)
    m['radcos'] = make_primitive("radcos", ['radians'], [], None, 1, process_radcos)
    m['radsin'] = make_primitive("radsin", ['radians'], [], None, 1, process_radsin)
    m['random'] = make_primitive("random", ['start'], ['end'], None, 1, process_random)
    m['readlist'] = make_primitive("readlist", [], [], None, 0, process_readlist)
    m['remainder'] = make_primitive("remainder", ['num1', 'num2'], [], None, 2, process_remainder)
    m['rl'] = m['readlist']
    m['remove'] = make_primitive("remove", ['thing', 'list'], [], None, 2, process_remove)
    m['remdup'] = make_primitive("remdup", ['list'], [], None, 1, process_remdup)
    m['repcount'] = make_primitive("repcount", [], [], None, 0, process_repcount)
    m['repeat'] = make_primitive("repeat", ['num', 'instructionlist'], [], None, 2, process_repeat)
    m['reverse'] = make_primitive("reverse", ['list'], [], None, 1, process_reverse)
    m['round'] = make_primitive("round", ['num'], [], None, 1, process_round)
    m['rseq'] = make_primitive("rseq", ['from', 'to', 'count'], [], None, 3, process_rseq)
    m['run'] = make_primitive("run", ['instructionlist'], [], None, 1, process_run)
    m['runresult'] = make_primitive("runresult", ['instructionlist'], [], None, 1, process_runresult)
    m['sentence'] = make_primitive("sentence", ['thing'], [], 'others', 2, process_sentence)
    m['se'] = m["sentence"]
    m['show'] = make_primitive("show", ['thing'], [], 'others', 1, process_show)
    m['sin'] = make_primitive("sin", ['degrees'], [], None, 1, process_sin)
    m['sqrt'] = make_primitive("sqrt", ['num'], [], None, 1, process_sqrt)
    m['stop'] = make_primitive("stop", [], [], None, 0, process_stop)
    m['substringp'] = make_primitive("substringp", ['thing1', 'thing2'], [], None, 2, process_substringp)
    m['substring?'] = m['substringp']
    m['sum'] = make_primitive("sum", ['num1', 'num2'], [], 'nums', 2, process_sum)
    m['thing'] = make_primitive("thing", ['thing'], [], None, 1, process_thing)
    m['type'] = make_primitive("type", ['thing'], [], 'others', 1, process_type)
    m['unicode'] = make_primitive("unicode", ['char'], [], None, 1, process_unicode)
    m['uppercase'] = make_primitive("uppercase", ['word'], [], None, 1, process_uppercase)
    m['while'] = make_primitive("while", ['tfexpr', 'instrlist'], [], None, 2, process_while)
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

def process_dot_eq(logo, thing1, thing2):
    """
    The .EQ command.
    """
    if thing1 is thing2:
        return 'true'
    else:
        return 'false'

def process_and(logo, *args):
    """
    The AND command.
    """
    truth_map = {'true': True, 'false': False}
    for arg in args:
        if not arg in truth_map:
            raise errors.LogoError("AND expects true/false values but received `{}` instead.".format(arg))
        if not truth_map[arg]:
            return 'false'
    return 'true'

def process_arctan(logo, *args):
    """
    The ARCTAN command.
    """
    if len(args) == 1:
        x = args[0]
        try:
            return (math.arctan(x) * 180) / math.pi
        except (TypeError, ValueError):
            raise errors.LogoError("ARCTAN expected a number, but got `{}` instead.".format(x))
    elif len(args) == 2:
        x = args[0]
        y = args[1]
        if x != 0:
            try:
                return (math.arctan(y / x) * 180) / math.pi
            except (TypeError, ValueError):
                raise errors.LogoError("ARCTAN expected a number, but got `{}` instead.".format(x))
        else:
            if y < 0:
                return -90
            elif y > 0:
                return 90
            else:
                raise ZeroDivisionError()

def process_beforep(logo, word1, word2):
    """
    The BEFOREP command.
    """
    dtype1 = _datatypename(word1)
    dtype2 = _datatypename(word2)
    for dtype in (dtype1, dtype2):
        if dtype != 'word':
            raise errors.LogoError("BEFOREP expects a word but got {} instead.".format(dtype))
    if str(word1) < str(word2):
        return 'true'
    else:
        return 'false'

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

def process_char(logo, codepoint):
    """
    The CHAR command.
    """
    try:
        return chr(codepoint)
    except TypeError:   
        raise errors.LogoError("CHAR expects an integer, but got `{}` instead.".format(codepoint))

def process_combine(logo, thing1, thing2):
    """
    The COMBINE command.
    """
    if _datatypename(thing2) in ('list'):
        return process_fput(logo, thing1, thing2)
    else:
        return process_word(logo, thing1, thing2)

def process_cos(logo, degrees):
    """
    The COS command.
    """
    try:
        return math.cos((degrees * math.pi) / 180.0)
    except (TypeError, ValueError):
        raise errors.LogoError("COS expected a number in degrees, but got `{}` instead.".format(degrees))

def process_count(logo, thing):
    """
    The COUNT command.
    """
    try:
        return len(thing)
    except TypeError:
        return len(str(thing))

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

def process_difference(logo, num1, num2):
    """
    The DIFFERENCE command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("DIFFERENCE expected a number but got `{}` instead.".format(arg))
    return num1 - num2

def process_dowhile(logo, instrlist, tfexpr):
    """
    The DO.WHILE command.
    """
    while True:
        _process_run_like("DO.WHILE", logo, instrlist)
        if _process_run_like("DO.WHILE", logo, tfexpr) == 'false':
            break

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

def process_exp(logo, num):
    """
    The EXP command.
    """
    try:
        return math.exp(num)
    except ValueError:
        raise errors.LogoError("EXP expected a number, but received `{}` instead.".format(num))

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

def process_for(logo, forcontrol, instrlist):
    """
    The FOR command.
    """
    for arg in (forcontrol, instrlist):
        dtype = _datatypename(arg)
        if dtype != 'list':
            raise errors.LogoError("FOR expects a list but received `{}` instead.".format(arg))
    if len(forcontrol) not in (3, 4):
        raise errors.LogoError("FOR expects a control list with 3 or 4 members, but received `{}` instead.".format(forcontrol))
    counter_name = forcontrol[0]
    start = _process_run_like("FOR", logo, forcontrol[1])
    limit = _process_run_like("FOR", logo, forcontrol[2])
    if len(forcontrol) == 4:
        step = _process_run_like("FOR", logo, forcontrol[3])
    else:
        if start <= limit:
            step = 1
        else:
            step = -1
    sign = functools.partial(math.copysign, 1)
    for_scope = {counter_name: start} 
    logo.scope_stack.append(for_scope)
    while sign(for_scope[counter_name] - limit)  != sign(step) or for_scope[counter_name] == limit:
        _process_run_like("FOR", logo, instrlist) 
        for_scope[counter_name] += step 
    logo.scope_stack.pop()

def process_fput(logo, thing, lst):
    """
    The FPUT command.
    """
    l = [thing]
    l.extend(lst)
    return l

def process_greaterequalp(logo, num1, num2):
    """
    The GREATEREQUALP command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("GREATEREQUALP expects numbers, but received `{}` instead.".format(arg))
    if num1 >= num2:
        return 'true'
    else:
        return 'false'

def process_greaterp(logo, num1, num2):
    """
    The GREATERP command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("GREATERP expects numbers, but received `{}` instead.".format(arg))
    if num1 > num2:
        return 'true'
    else:
        return 'false'

def process_if(logo, tf, instrlist, instrlist2=None):
    """
    The IF command.
    """
    try:
        tf = tf.lower()
    except AttributeError:
        raise errors.LogoError("IF expects TRUE/FALSE but received `{}` instead.".format(tf))
    if not tf in ('true', 'false'):
        raise errors.LogoError("IF expects TRUE/FALSE but received `{}` instead.".format(tf))
    dtype = _datatypename(instrlist)
    if dtype != 'list':
        raise errors.LogoError("IF expects instructionlist but received `{}` instead.".format(instrlist))
    if instrlist2 is not None:
        dtype2 = _datatypename(instrlist2)
        if dtype != 'list':
            raise errors.LogoError("IF expects instructionlist but received `{}` instead.".format(instrlist2))
    if tf == 'true':
        script = _list_contents_repr(instrlist, include_braces=False)
        return logo.process_instructionlist(script) 
    elif instrlist2 != None:
        script = _list_contents_repr(instrlist2, include_braces=False)
        return logo.process_instructionlist(script) 

def process_ifelse(logo, tf, instrlist1, instrlist2):
    """
    The IFELSE command.
    """
    try:
        tf = tf.lower()
    except AttributeError:
        raise errors.LogoError("IFELSE expects TRUE/FALSE but received `{}` instead.".format(tf))
    if not tf in ('true', 'false'):
        raise errors.LogoError("IFELSE expects TRUE/FALSE but received `{}` instead.".format(tf))
    for instrlist in (instrlist1, instrlist2):
        dtype = _datatypename(instrlist)
        if dtype != 'list':
            raise errors.LogoError("IF expects instructionlist but received `{}` instead.".format(instrlist))
    if tf == 'true':
        script = _list_contents_repr(instrlist1, include_braces=False)
        return logo.process_instructionlist(script) 
    else:
        script = _list_contents_repr(instrlist2, include_braces=False)
        return logo.process_instructionlist(script) 

def process_ignore(logo, value):
    """
    The IGNORE command.
    """
    return

def process_int(logo, num):
    """
    The INT command.
    """
    if not isinstance(num, numbers.Number):
        raise errors.LogoError("INT expects a number but received `{}`.".format(num))
    return int(num)

def process_iseq(logo, frm, to):
    """
    The ISEQ command.
    """
    if frm <= to:
        start = frm
        stop = to + 1
        step = 1
    else:
        start = frm
        stop = to - 1
        step = -1
    try:
        return list(range(start, stop, step)) 
    except TypeError:
        raise errors.LogoError("ISEQ expects numbers, but received `{}`, `{}` instead.".format(frm, to))

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

def process_lessequalp(logo, num1, num2):
    """
    The LESSEQUALP command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("LESSEQUALP expects numbers, but received `{}` instead.".format(arg))
    if num1 <= num2:
        return 'true'
    else:
        return 'false'

def process_lessp(logo, num1, num2):
    """
    The LESSP command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("LESSP expects numbers, but received `{}` instead.".format(arg))
    if num1 < num2:
        return 'true'
    else:
        return 'false'

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

def process_local(logo, *args):
    """
    The LOCAL command.
    """
    scope = logo.scope_stack[-1]
    if len(args) == 1:
        arg = args[0]
        dtype = _datatypename(arg)
        if dtype == 'word':
            scope[arg] = None
        elif dtype == 'list':
            for varname in arg:
                dtype2 = _datatypename(varname)
                if dtype2 != 'word':
                    raise errors.LogoError("LOCAL expects a list of words, but received `{}` instead.".format(varname))
                scope[varname] = None
        else:
            raise errors.LogoError("LOCAL expects a word or a list or words, but received `{}` instead.".format(arg))
    else:
        for varname in args:
            dtype = _datatypename(varname)
            if dtype != 'word':
                raise errors.LogoError("LOCAL expects a list of words, but received `{}` instead.".format(varname))
            scope[varname] = None
     
def process_localmake(logo, varname, value):
    """
    The LOCALMAKE command.
    """
    scope = logo.scope_stack[-1]
    scope[varname] = value

def process_log10(logo, num):
    """
    The LOG10 command.
    """
    try:
        return math.log10(num)
    except ValueError:
        raise errors.LogoError("LOG10 expected a number, but received `{}` instead.".format(num))

def process_lowercase(logo, word):
    """
    The LOWERCASE command.
    """
    try:
        return word.lower()
    except AttributeError:
        raise errors.LogoError("LOWERCASE expected a word but got a {} instead.".format(_datatypename(word)))

def process_ln(logo, num):
    """
    The LN command.
    """
    try:
        return math.log(num)
    except ValueError:
        raise errors.LogoError("LN expected a number, but received `{}` instead.".format(num))

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
    scopes = logo.scope_stack
    for scope in reversed(scopes):
        if varname in scope:
            scope[varname] = value
            return
    global_scope = logo.scope_stack[0]
    global_scope[varname] = value 

def process_member(logo, thing1, thing2):
    """
    The MEMBER command.
    """
    dtype1 = _datatypename(thing1)
    dtype2 = _datatypename(thing2)
    if dtype1 == dtype2 == 'word':
        value2 = str(thing2)
        value1 = str(thing1)
        i = value2.find(value1)
        if i == -1:
            return ""
        else:
            return value2[i:]
    elif dtype2 == 'word':
        return ""
    elif dtype2 == 'list':
        try:
            return thing2[thing2.index(thing1):]
        except ValueError:
            return []
    else:
        raise errors.LogoError("MEMBER expects a word or list for thing2 but got a {}.".format(dtype2))

def process_memberp(logo, thing1, thing2):
    """
    The MEMBERP command.
    """
    if thing1 in thing2:
        return 'true'
    else:
        return 'false'

def process_modulo(logo, num1, num2):
    """
    The MODULO command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("MODULO expected a number but got `{}` instead.".format(arg))
    absval = abs(num1 % num2)
    if num2 < 0:
        return -absval
    else:
        return absval

def process_not(logo, tf):
    """
    The NOT command.
    """
    if tf == 'true':
        return 'false'
    elif tf == 'false':
        return 'true'
    else:
        raise errors.LogoError("AND expects true/false values but received `{}` instead.".format(arg))

def process_notequalp(logo, thing1, thing2):
    """
    The NOTEQUALP command.
    """
    if thing1 != thing2:
        return 'true'
    else:
        return 'false'

def process_numberp(logo, thing):
    """
    The NUMBERP command.
    """
    if isinstance(thing, numbers.Number):
        return 'true'
    else:
        return 'false'

def process_or(logo, *args):
    """
    The OR command.
    """
    truth_map = {'true': True, 'false': False}
    for arg in args:
        if not arg in truth_map:
            raise errors.LogoError("OR expects true/false values but received `{}` instead.".format(arg))
        if truth_map[arg]:
            return 'true'
    return 'false'

def process_output(logo, value):
    """
    The OUTPUT command.
    """
    raise errors.OutputSignal(value)

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

def process_power(logo, num1, num2):
    """
    The POWER command.
    """
    try:
        return math.pow(num1, num2)
    except ValueError:
        raise errors.LogoError("POWER expected a number, but received [{}, {}] instead.".format(num1, num2))

def process_print(logo, *args):
    """
    The PRINT command.
    """
    reps = []
    for arg in args:
        if _datatypename(arg) == 'list':
            reps.append(_list_contents_repr(arg, include_braces=False, escape_delimiters=False))
        elif _datatypename(arg) == 'word':
            reps.append(str(arg))
    print(' '.join(reps))

def process_product(logo, *args):
    """
    The PRODUCT command.
    """
    for arg in args:
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("PRODUCT expected a number but got `{}` instead.".format(arg))
    return functools.reduce(operator.mul, args)

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

def process_quotient(logo, num1, num2):
    """
    The QUOTIENT command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("QUOTIENT expected a number but got `{}` instead.".format(arg))
    return num1 / num2

def process_radarctan(logo, *args):
    """
    The RADARCTAN command.
    """
    if len(args) == 1:
        x = args[0]
        try:
            return math.arctan(x)
        except (TypeError, ValueError):
            raise errors.LogoError("RADARCTAN expected a number, but got `{}` instead.".format(x))
    elif len(args) == 2:
        x = args[0]
        y = args[1]
        if x != 0:
            try:
                return math.arctan(y / x)
            except (TypeError, ValueError):
                raise errors.LogoError("RADARCTAN expected a number, but got `{}` instead.".format(x))
        else:
            if y < 0:
                return -(math.pi / 2.0)
            elif y > 0:
                return (math.pi / 2.0)
            else:
                raise ZeroDivisionError()

def process_radcos(logo, radians):
    """
    The RADCOS command.
    """
    try:
        return math.cos(radians)
    except (TypeError, ValueError):
        raise errors.LogoError("RADCOS expected a number in radians, but got `{}` instead.".format(radians))

def process_radsin(logo, radians):
    """
    The RADSIN command.
    """
    try:
        return math.sin(radians)
    except (TypeError, ValueError):
        raise errors.LogoError("RADSIN expected a number in radians, but got `{}` instead.".format(radians))

def process_random(logo, *args):
    """
    The RANDOM command.
    """
    if len(args) == 1:
        try:
            return random.randrange(0, args[0])
        except ValueError:
            raise errors.LogoError("RANDOM expects a non-negative integer, but received `{}` instead.".format(args[0]))
    else:
        try:
            return random.randint(args[0], args[1])
        except ValueError:
            raise errors.LogoError("RANDOM expects integers `start` <= `end` but received `{}`, `{}` instead.".format(args[0], args[1]))

def process_readlist(logo):
    """
    The READLIST command.
    """
    data = input()
    data = "[{}]".format(data)
    lst = logo.evaluate_readlist(data)
    return lst

def process_remainder(logo, num1, num2):
    """
    The REMAINDER command.
    """
    for arg in (num1, num2):
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("REMAINDER expected a number but got `{}` instead.".format(arg))
    absval = abs(num1 % num2)
    if num1 < 0:
        return -absval
    else:
        return absval

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

def process_repcount(logo):
    """
    The REPCOUNT command.
    """
    return logo.get_repcount()

def process_repeat(logo, num, instructionlist):
    """
    The REPEAT command.
    """
    if not isinstance(num, numbers.Number):
        raise errors.LogoError("REPEAT expects a number and an instructionlist, but received `{}` instead.".format(num))
    dtype = _datatypename(instructionlist)
    if dtype != 'list':
        raise errors.LogoError("REPEAT expects a number and an instructionlist, but received `{}` instead.".format(instructionlist))
    logo.create_repcount_scope()
    for i in range(num):
        logo.set_repcount(i + 1)
        script = _list_contents_repr(instructionlist, include_braces=False)
        logo.process_instructionlist(script) 
    logo.destroy_repcount_scope()

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

def process_round(logo, num):
    """
    The ROUND command.
    """
    try:
        return round(num)
    except TypeError:
        raise errors.LogoError("ROUND expects a number, but received `{}` instead.".format(num))

def process_rseq(logo, frm, to, count):
    """
    The RSEQ command.
    """
    pos_fn = lambda frm, to, count, i: (to * i + frm * (count - i - 1)) / (count - 1)
    p = functools.partial(pos_fn, frm, to, count)
    try:
        return list(map(p, range(count)))
    except TypeError:
        raise errors.LogoError("RSEQ expected numbers, but got `{}`, `{}`, `{}` instead.".format(frm, to, count))

def process_run(logo, instructionlist):
    """
    The RUN command.
    """
    return _process_run_like("RUN", logo, instructionlist)

def process_runresult(logo, instructionlist):
    """
    The RUNRESULT command.
    """
    result = _process_run_like("RUNRESULT", logo, instructionlist)
    if result is None:
        return []
    else:
        return [result]

def _process_run_like(cmd, logo, instructionlist):
    dtype = _datatypename(instructionlist)
    if dtype == 'list':
        script = _list_contents_repr(instructionlist, include_braces=False)
        return logo.process_instructionlist(script) 
    elif dtype == 'word':
        return logo.process_instructionlist(str(instructionlist))
    else:
        raise errors.LogoError("{} expects a word or list, but received `{}` instead.".format(cmd, instructionlist))

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

def process_sin(logo, degrees):
    """
    The SIN command.
    """
    try:
        return math.sin((degrees * math.pi) / 180.0)
    except (TypeError, ValueError):
        raise errors.LogoError("SIN expected a number in degrees, but got `{}` instead.".format(degrees))

def process_sqrt(logo, num):
    """
    The SQRT command.
    """
    try:
        return math.sqrt(num)
    except TypeError:
        raise errors.LogoError("SQRT expects a number, but received `{}` instead.".format(num))
    except ValueError as ex:
        raise errors.LogoError("SQRT expects a non-negative number, but received `{}` instead.".format(num))

def process_stop(logo):
    """
    The STOP command.
    """
    raise errors.StopSignal()

def process_substringp(logo, thing1, thing2):
    """
    The SUBSTRINGP command.
    """
    for thing in (thing1, thing2):
        dtype = _datatypename(thing)
        if dtype != 'word':
            raise errors.LogoError("SUBSTRINGP expects a word, but got a {} instead.".format(dtype))
    if str(thing1) in str(thing2):
        return 'true'
    else:
        return 'false'

def process_sum(logo, *args):
    """
    The SUM command.
    """
    for arg in args:
        if not isinstance(arg, numbers.Number):
            raise errors.LogoError("SUM expected a number but got `{}` instead.".format(arg))
    return sum(args)

def process_thing(logo, varname):
    """
    The THING command.
    """
    return logo.get_variable_value(varname) 

def process_type(logo, *args):
    """
    The TYPE command.
    """
    reps = []
    for arg in args:
        if _datatypename(arg) == 'list':
            reps.append(_list_contents_repr(arg, include_braces=False))
        elif _datatypename(arg) == 'word':
            reps.append(str(arg))
    print(' '.join(reps), end="")

def process_unicode(logo, char):
    """
    The UNICODE command.
    """
    try:
        return ord(char)
    except TypeError:
        raise errors.LogoError("UNICODE expects a single character, but got `{}`.".format(char))

def process_uppercase(logo, word):
    """
    The UPPERCASE command.
    """
    try:
        return word.upper()
    except AttributeError:
        raise errors.LogoError("UPPERCASE expected a word but got a {} instead.".format(_datatypename(word)))

def process_while(logo, tfexpr, instrlist):
    """
    The WHILE command.
    """
    while _process_run_like("WHILE", logo, tfexpr) == 'true':
        _process_run_like("WHILE", logo, instrlist)

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

def process_show(logo, *args):
    """
    The SHOW command.
    """
    reps = []
    for arg in args:
        dtype = _datatypename(arg)
        if dtype == 'list':
            reps.append(_list_contents_repr(arg, escape_delimiters=False))
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

def _datatypename(o):
    """
    Returns a sting corresponding to the Logo data type name.
    """
    if isinstance(o, str) or isinstance(o, numbers.Number):
        return 'word'
    if isinstance(o, list):
        return 'list'
    return 'unknown'

def _list_contents_repr(o, include_braces=True, escape_delimiters=True):
    dtype = _datatypename(o)
    if dtype == 'list':
        rep = ' '.join([_list_contents_repr(x, escape_delimiters=escape_delimiters) for x in o])
        if include_braces:
            rep = "[{}]".format(rep)
        return rep
    elif dtype == 'word':
        if escape_delimiters:
            return _escape_word_chars(str(o))
        else:
            return str(o)
    else:
        raise errors.LogoError("Unknown data type for `{}`.".format(o))

def _escape_word_chars(word):
    chars = []
    for c in word:
        if c in (' ', ';', '\\', '[', ']'):
            c = r"\{}".format(c)
        chars.append(c)
    return ''.join(chars)

