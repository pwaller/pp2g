import ast
import os

from textwrap import dedent


def indent(t, depth=1):
    """
    Reverse of dedent
    """
    spacing = "    " * depth
    return t.replace("\n", "\n" + spacing)

import name


class Node(object):
    pass


def skip(node: Node, ctx):
    print("// skipped {}".format(node))


def name_(node: ast.Name, ctx):
    if isinstance(ctx, ClassDef) and node.id == "self":
        return ctx.name[0].lower()
    return name.var_to_camel(node.id)


def str_(node: ast.Str, ctx):
    return '"{}"'.format(node.s)


def aug_assign(node: ast.AugAssign, ctx):
    ops = {"Add": "+", "Sub": "-", "Mult": "*", "Div": "/", "Mod": "%",
           "LShift": "<<", "RShift": ">>", "BitOr": "|", "BitXor": "^",
           "BitAnd": "&", "FloorDiv": "//", "Pow": "**"}
    op = ops[node.op.__class__.__name__]
    tgt = dispatch(node.target, ctx)
    value = dispatch(node.value, ctx)
    return "{} {}= {}".format(tgt, op, value)


def assign(node: ast.Assign, ctx):
    fmt = "{} = {}"
    if ctx == module:
        fmt = "var {}".format(fmt)
    tgts = [dispatch(t, ctx) for t in node.targets]
    return fmt.format(", ".join(tgts), dispatch(node.value, ctx))


def num(node: ast.Num, ctx):
    return "{}".format(node.n)


def attribute(node: ast.Attribute, ctx):
    return "{}.{}".format(dispatch(node.value, ctx), node.attr)


def lst(node: ast.List, ctx):
    return "[{}]".format(", ".join(dispatch(e, ctx) for e in node.elts))


def arg_type(node: Node, ctx):
    # def default(node):
    #     return "python.Type"
    #
    # def lst(node: ast.List):
    #     assert len(node.elts) == 1, "multiply typed list"
    #     (typ,) = node.elts
    #     return "[]{}".format(arg_type(typ))

    typ = dispatch(node, ctx)

    mapping = {
        "str": "string",
    }

    return mapping.get(typ, typ)


def arg(node: ast.arg, ctx):
    typ = "python.Type"
    if node.annotation:
        typ = dispatch(node.annotation, ctx)

    return "{} {}".format(
        name.var_to_camel(node.arg),
        # dispatch(node.arg, ctx),
        typ,
    )


def arguments(node: ast.arguments, ctx):
    return ", ".join(dispatch(n, ctx) for n in node.args)


def returns(node: Node, ctx):  # -> str:
    # TODO(pwaller): implement return type
    return ""


def expr(node: ast.Expr, ctx):
    return dispatch(node.value, ctx)


def call(node: ast.Call, ctx):
    func = dispatch(node.func, ctx)
    args = [dispatch(a, ctx) for a in node.args]
    for k in node.keywords:
        args.append(dispatch(k, ctx))
    if node.starargs:
        args.append("*" + dispatch(node.starargs, ctx))
    return "{}({})".format(func, ", ".join(args))
    # return "// TODO call {}".format(dispatch(node.func))


def return_(node: ast.Return, ctx):
    if node.value is None:
        return "return"
    expr = dispatch(node.value, ctx)
    if isinstance(node.value, ast.Tuple):
        expr = expr[1:-1]
    return "return {}".format(expr)


def binop(node: ast.BinOp, ctx):
    ops = {"Add": "+", "Sub": "-", "Mult": "*", "Div": "/", "Mod": "%",
           "LShift": "<<", "RShift": ">>", "BitOr": "|", "BitXor": "^",
           "BitAnd": "&", "FloorDiv": "//", "Pow": "**"}

    l = dispatch(node.left, ctx)
    o = ops[node.op.__class__.__name__]
    r = dispatch(node.right, ctx)
    return "{} {} {}".format(l, o, r)


def break_(node: ast.Break, ctx):
    return "break"


def continue_(node: ast.Continue, ctx):
    return "continue"


def is_enumerate(node: Node, ctx):
    if isinstance(node, ast.Expr):
        return is_enumerate(node.value)
    if not isinstance(node, ast.Call):
        return False
    name = dispatch(node.func, ctx)
    return name == "enumerate"


def remove_enumerate(node: Node, ctx):
    return dispatch(node.args[0], ctx)


def for_(node: ast.For, ctx):
    fmt = dedent("""\
        for {loop} {{
            {body}
        }}
    """).rstrip()

    tgt = dispatch(node.target, ctx)

    if is_enumerate(node.iter, ctx):
        itr = remove_enumerate(node.iter, ctx)
        l = "{} := range {}".format(tgt[1:-1], itr)
    else:
        l = "_, {} := range {}".format(tgt, dispatch(node.iter, ctx))

    b = node.body

    return fmt.format(
        loop=l,
        body=indent(body(node.body, ctx)),
    )


def if_(node: ast.If, ctx):
    fmt = dedent("""\
        if {test} {{
            {body}
        }}
    """).rstrip("\n")

    return fmt.format(
        test=dispatch(node.test, ctx),
        body=indent(body(node.body, ctx)),
    )


def name_constant(node: ast.NameConstant, ctx):
    if node.value is None:
        return "None"
    if node.value is True:
        return "true"
    if node.value is False:
        return "false"
    return dispatch(node.value, ctx)


def tuple_(node: ast.Tuple, ctx):
    elements = ", ".join(dispatch(e, ctx) for e in node.elts)
    return "({})".format(elements)


def comprehension(node, ctx):
    result = []
    l = result.append
    l(" for ")
    part = dispatch(node.target, ctx)
    if isinstance(node.target, ast.Tuple):
        part = part[1:-1]
    l(part)
    l(" in ")
    l(dispatch(node.iter, ctx))
    for clause in node.ifs:
        l(" if ")
        l(dispatch(clause, ctx))
    return "".join(result)


def dict_(node: ast.Dict, ctx):
    def item(k, v):
        return "{}: {}".format(dispatch(k, ctx), dispatch(v, ctx))
    body = ", ".join(item(k, v) for k, v in zip(node.keys, node.values))
    return "map[interface{{}}]interface{{}}{{{}}}".format(body)


def compare(node: ast.Compare, ctx):
    cmpops = {
        "Eq": "==", "NotEq": "!=", "Lt": "<", "LtE": "<=", "Gt": ">", "GtE": ">=",
        "Is": "is", "IsNot": "is not", "In": "in", "NotIn": "not in",
    }
    result = []
    result.append(dispatch(node.left, ctx))
    for o, e in zip(node.ops, node.comparators):
        result.append(cmpops[o.__class__.__name__])
        result.append(dispatch(e, ctx))
    return " ".join(result)


def unaryop(node: ast.UnaryOp, ctx):
    unops = {"Invert": "~", "Not": "!", "UAdd": "+", "USub": "-"}
    op = unops[node.op.__class__.__name__]

    return "{}{}".format(op, dispatch(node.operand, ctx))


def boolop(node: ast.BoolOp, ctx):
    boolops = {ast.And: '&&', ast.Or: '||'}
    op = boolops[type(node.op)]
    inter = " {} ".format(op)
    return inter.join(dispatch(o, ctx) for o in node.values)


def list_comp(node: ast.ListComp, ctx):
    return "[{}]".format(generator_exp(node, ctx))


def generator_exp(node: ast.GeneratorExp, ctx):
    f = dispatch(node.elt, ctx)
    gens = []
    for g in node.generators:
        gens.append(dispatch(g, ctx))
    return "{}{}".format(f, "".join(gens))


def subscript(node: ast.Subscript, ctx):
    v = dispatch(node.value, ctx)
    s = dispatch(node.slice, ctx)
    return "{}[{}]".format(v, s)


def assert_(node: ast.Assert, ctx):
    return "// assert {}".format(dispatch(node.test, ctx))


def slice_(node: ast.Slice, ctx):
    result = []
    l = result.append
    if node.lower:
        l(dispatch(node.lower, ctx))
    l(":")
    if node.upper:
        l(dispatch(node.upper, ctx))
    if node.step:
        l(":")
        l(dispatch(node.step, ctx))
    return "".join(result)


def index_(node: ast.Index, ctx):
    return dispatch(node.value, ctx)


def body(nodes: [Node], ctx):  # -> str:
    ret = []
    for node in nodes:
        # ret.append("// {}".format(node))
        ret.append(dispatch(node, ctx))

    return "\n".join(ret)


def parse_docstring(node: ast.FunctionDef):
    first = node.body[0]
    if not isinstance(first, ast.Expr):
        return "", node.body
    value = first.value
    if not isinstance(value, ast.Str):
        return "", node.body
    s = "\n// {}".format(value.s.strip().replace("\n", "\n// "))
    return s, node.body[1:]


def function_def(node: ast.FunctionDef, ctx):

    n = cls = ""
    newctx = function_def

    name_ = name.to_camel(node.name)
    fmt = dedent("""\
        {docstring}
        func {name}({args}) {returns}{{
            {body}
        }}
    """).rstrip("\n")

    # Closure
    if ctx is function_def:
        name_ = name.var_to_camel(node.name)
        fmt = dedent("""\
            {docstring}
            {name} := func({args}) {returns}{{
                {body}
            }}
        """).rstrip("\n")
    elif isinstance(ctx, ClassDef):
        name_ = name.var_to_camel(node.name)
        fmt = dedent("""\
            {docstring}
            func ({n} *{cls}) {name}({args}) {returns}{{
                {body}
            }}
        """).rstrip("\n")
        cls = ctx.name
        n = ctx.name[0].lower()
        newctx = ctx

    s, b = parse_docstring(node)

    return fmt.format(
        name=name_,
        args=dispatch(node.args, ctx),
        returns=returns(node.returns, ctx),
        docstring=s,
        body=indent(body(b, newctx)),
        cls=cls,
        n=n,
    )


def lambda_(node: ast.Lambda, ctx):
    args = dispatch(node.args, ctx)
    expr = dispatch(node.body, ctx)

    fmt = "func({}) {{ return {} }}"
    return fmt.format(args, expr)


class ClassDef(object):

    def __init__(self, name):
        self.name = name


def class_def(node: ast.ClassDef, ctx):
    s, b = parse_docstring(node)
    result = []
    if s:
        result.append(s)
    result.append("type {} struct {{}}".format(node.name))
    result.append(body(b, ClassDef(node.name)))
    return "\n".join(result)


def yield_(node, ctx):
    return "// yield {}".format(dispatch(node.value, ctx))


def keyword(node: ast.keyword, ctx):
    # arg = dispatch(node.arg, ctx)
    value = dispatch(node.value, ctx)
    return "{}={}".format(node.arg, value)


def dispatch(node: Node, ctx):
    def unknown(node, ctx):
        return "// unknown {}{}".format(type(node).__name__, node._fields)

    fn = {
        ast.Expr: expr,
        ast.Attribute: attribute,
        ast.If: if_,
        ast.UnaryOp: unaryop,
        ast.BoolOp: boolop,
        ast.BinOp: binop,
        ast.Compare: compare,
        ast.Call: call,
        ast.Name: name_,
        ast.Return: return_,
        ast.Num: num,
        ast.NameConstant: name_constant,
        ast.Str: str_,
        ast.List: lst,
        ast.Tuple: tuple_,
        ast.Dict: dict_,
        ast.Assign: assign,
        ast.For: for_,
        ast.Break: break_,
        ast.Continue: continue_,
        ast.FunctionDef: function_def,
        ast.ClassDef: class_def,
        ast.Lambda: lambda_,
        ast.ListComp: list_comp,
        ast.GeneratorExp: generator_exp,
        ast.Subscript: subscript,
        ast.comprehension: comprehension,
        ast.arguments: arguments,
        ast.arg: arg,
        ast.Assert: assert_,
        ast.Slice: slice_,
        ast.Index: index_,
        ast.Yield: yield_,
        ast.AugAssign: aug_assign,
        ast.keyword: keyword,
    }.get(type(node), unknown)

    return fn(node, ctx)


def module(pkg_name: str, module_node: ast.Module, ctx=None):
    """Translate a module"""

    print("package {}".format(name.package(pkg_name)))
    print()

    for node in module_node.body:
        print(dispatch(node, ctx=module))
