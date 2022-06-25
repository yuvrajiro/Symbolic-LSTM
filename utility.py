import sympy as sp



OPERATORS = {
    # Relational functions
    'lessthan': 2,
    # Elementary functions
    'add': 2,
    'sub': 2,
    'mul': 2,
    'div': 2,
    'pow': 2,
    'rac': 2,
    'inv': 1,
    'pow2': 1,
    'pow3': 1,
    'pow4': 1,
    'pow5': 1,
    'sqrt': 1,
    'exp': 1,
    'ln': 1,
    'abs': 1,
    'sign': 1,
    # Trigonometric Functions
    'sin': 1,
    'cos': 1,
    'tan': 1,
    'cot': 1,
    'sec': 1,
    'csc': 1,
    # Trigonometric Inverses
    'asin': 1,
    'acos': 1,
    'atan': 1,
    'acot': 1,
    'asec': 1,
    'acsc': 1,
    # Hyperbolic Functions
    'sinh': 1,
    'cosh': 1,
    'tanh': 1,
    'coth': 1,
    'sech': 1,
    'csch': 1,
    # Hyperbolic Inverses
    'asinh': 1,
    'acosh': 1,
    'atanh': 1,
    'acoth': 1,
    'asech': 1,
    'acsch': 1,
    # custom functions
    'f': 1,
    'g': 2,
    'h': 3,
}

operators = sorted(list(OPERATORS.keys()))

SYMPY_OPERATORS = {
    # Relational functions
    sp.StrictLessThan: 'lessthan',
    # Elementary functions
    sp.Add: 'add',
    sp.Mul: 'mul',
    sp.Pow: 'pow',
    sp.exp: 'exp',
    sp.log: 'ln',
    sp.Abs: 'abs',
    sp.sign: 'sign',
    # Trigonometric Functions
    sp.sin: 'sin',
    sp.cos: 'cos',
    sp.tan: 'tan',
    sp.cot: 'cot',
    sp.sec: 'sec',
    sp.csc: 'csc',

}

variable = {'x': sp.Symbol('x', real=True, nonzero=True)}


def _sympy_to_prefix(op, expr):
    """
    Parse a SymPy expression given an initial root operator.
    """
    n_args = len(expr.args)

    assert (op=='add' or op=='mul') and (n_args >= 2) or (op!='add' and op!='mul') and (1 <= n_args <= 2)

    # square root
    if op=='pow' and isinstance(expr.args[1], sp.Rational) and expr.args[1].p==1 and expr.args[1].q==2:
        return ['sqrt'] + sympy_to_prefix(expr.args[0])

    # parse children
    parse_list = []
    for i in range(n_args):
        if i==0 or i < n_args - 1:
            parse_list.append(op)
        parse_list += sympy_to_prefix(expr.args[i])

    return parse_list


def write_int(val):
    """
    Convert a decimal integer to a representation in the given base.
    The base can be negative.
    In balanced bases (positive), digits range from -(base-1)//2 to (base-1)//2
    """
    base = 10
    balanced = False
    res = []
    max_digit = abs(base)
    if balanced:
        max_digit = (base - 1) // 2
    else:
        if base > 0:
            neg = val < 0
            val = -val if neg else val
    while True:
        rem = val % base
        val = val // base
        if rem < 0 or rem > max_digit:
            rem -= base
            val += 1
        res.append(str(rem))
        if val==0:
            break
    if base < 0 or balanced:
        res.append('INT')
    else:
        res.append('INT-' if neg else 'INT+')
    return res[::-1]


def sympy_to_prefix(expr):
    """
    Convert a SymPy expression to a prefix one.
    """
    if isinstance(expr, sp.Symbol):
        return [str(expr)]
    elif isinstance(expr, sp.Integer):
        return write_int(int(str(expr)))
    elif isinstance(expr, sp.Rational):
        return ['div'] + write_int(int(expr.p)) + write_int(int(expr.q))
    elif expr==sp.E:
        return ['E']
    elif expr==sp.pi:
        return ['pi']
    elif expr==sp.I:
        return ['I']
    # SymPy operator
    for op_type, op_name in SYMPY_OPERATORS.items():
        if isinstance(expr, op_type):
            return _sympy_to_prefix(op_name, expr)
    # unknown operator
    raise Exception(f"Unknown SymPy operator: {expr}")


def parse_int(lst):
    """
    Parse a list that starts with an integer.
    Return the integer value, and the position it ends in the list.
    """
    base = 10
    balanced = False
    val = 0
    if not (balanced and lst[0]=='INT' or base >= 2 and lst[0] in ['INT+', 'INT-'] or base <= -2 and lst[0]=='INT'):
        raise Exception(f"Invalid integer in prefix expression")
    i = 0
    for x in lst[1:]:
        if not (x.isdigit() or x[0]=='-' and x[1:].isdigit()):
            break
        val = val * base + int(x)
        i += 1
    if base > 0 and lst[0]=='INT-':
        val = -val
    return val, i + 1


def _prefix_to_infix(expr):
    """
    Parse an expression in prefix mode, and output it in either:
      - infix mode (returns human readable string)
      - develop mode (returns a dictionary with the simplified expression)
    """
    if len(expr)==0:
        raise Exception("Empty prefix list.")
    t = expr[0]
    if t in operators:
        args = []
        l1 = expr[1:]
        for _ in range(OPERATORS[t]):
            i1, l1 = _prefix_to_infix(l1)
            args.append(i1)
        return write_infix(t, args), l1
    elif t in variable:
        return t, expr[1:]
    else:
        val, i = parse_int(expr)
        return str(val), expr[i:]


def prefix_to_infix(expr):
    """
    Prefix to infix conversion.
    """
    p, r = _prefix_to_infix(expr)
    if len(r) > 0:
        raise Exception(f"Incorrect prefix expression \"{expr}\". \"{r}\" was not parsed.")
    return f'({p})'


def write_infix(token, args):
    """
    Infix representation.
    Convert prefix expressions to a format that SymPy can parse.
    """
    if token=='add':
        return f'({args[0]})+({args[1]})'
    elif token=='sub':
        return f'({args[0]})-({args[1]})'
    elif token=='mul':
        return f'({args[0]})*({args[1]})'
    elif token=='div':
        return f'({args[0]})/({args[1]})'
    elif token=='pow':
        return f'({args[0]})**({args[1]})'
    elif token=='rac':
        return f'({args[0]})**(1/({args[1]}))'
    elif token=='abs':
        return f'Abs({args[0]})'
    elif token=='inv':
        return f'1/({args[0]})'
    elif token=='pow2':
        return f'({args[0]})**2'
    elif token=='pow3':
        return f'({args[0]})**3'
    elif token=='pow4':
        return f'({args[0]})**4'
    elif token=='pow5':
        return f'({args[0]})**5'
    elif token in ['sign', 'sqrt', 'exp', 'ln', 'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'asin', 'acos', 'atan',
                   'acot', 'asec', 'acsc', 'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch', 'asinh', 'acosh', 'atanh',
                   'acoth', 'asech', 'acsch']:
        return f'{token}({args[0]})'
    elif token=='derivative':
        return f'Derivative({args[0]},{args[1]})'
    elif token=='f':
        return f'f({args[0]})'
    elif token=='g':
        return f'g({args[0]},{args[1]})'
    elif token=='h':
        return f'h({args[0]},{args[1]},{args[2]})'
    elif token.startswith('INT'):
        return f'{token[-1]}{args[0]}'
    else:
        return token
    raise Exception(f"Unknown token in prefix expression: {token}, with arguments {args}")
