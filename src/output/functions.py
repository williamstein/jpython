# vim:fileencoding=utf-8
# License: BSD Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>
# globals:regenerate
from __python__ import hash_literals

from ast import AST_ClassCall, AST_New, has_calls, AST_Dot, AST_SymbolRef, is_node_type
from output.stream import OutputStream
from output.statements import print_bracketed
from output.utils import create_doctring
from output.operators import print_getattr

anonfunc = 'ρσ_anonfunc'
module_name = 'null'

def set_module_name(x):
    nonlocal module_name
    module_name = '"' + x + '"' if x else 'null'


# Function definition {{{

def decorate(decorators, output, func):
    pos = 0
    def wrap():
        nonlocal pos
        if pos < decorators.length:
            decorators[pos].expression.print(output)
            pos += 1
            output.with_parens(def():
                wrap()
            )
        else:
            func()
    wrap()

def function_args(argnames, output, strip_first):
    output.with_parens(def():
        if argnames and argnames.length and (argnames.is_simple_func is True or argnames.is_simple_func is undefined):
            for i, arg in enumerate((argnames.slice(1) if strip_first else argnames)):
                if i:
                    output.comma()
                arg.print(output)
    )
    output.space()

def function_preamble(node, output, offset):
    a = node.argnames
    if not a or a.is_simple_func:
        return
    # If this function has optional parameters/*args/**kwargs declare it differently
    fname = node.name.name if node.name else anonfunc
    kw = 'arguments[arguments.length-1]'
    # Define all formal parameters
    for c, arg in enumerate(a):
        i = c - offset
        if i >= 0:
            output.indent()
            output.print("var")
            output.space()
            output.assign(arg)
            if Object.prototype.hasOwnProperty.call(a.defaults, arg.name):
                output.spaced('(arguments[' + i + ']', '===', 'undefined', '||',
                                '(', i, '===', 'arguments.length-1', '&&', kw, '!==', 'null', '&&', 'typeof', kw, '===', '"object"', '&&',
                                kw, '[ρσ_kwargs_symbol]', '===', 'true))', '?', '')
                output.print(fname + '.__defaults__.'), arg.print(output)
                output.space(), output.print(':'), output.space()
            else:
                output.spaced('(', i, '===', 'arguments.length-1', '&&', kw, '!==', 'null', '&&', 'typeof', kw, '===', '"object"', '&&',
                                kw, '[ρσ_kwargs_symbol]', '===', 'true)', '?', 'undefined', ':', '')
            output.print('arguments[' + i + ']')
            output.end_statement()
    if a.kwargs or a.has_defaults:
        # Look for an options object
        kw = a.kwargs.name if a.kwargs else 'ρσ_kwargs_obj'
        output.indent()
        output.spaced('var', kw, '=', 'arguments[arguments.length-1]')
        output.end_statement()
        # Ensure kwargs is the options object
        output.indent()
        output.spaced('if', '(' + kw, '===', 'null', '||', 'typeof', kw, '!==', '"object"', '||', kw, '[ρσ_kwargs_symbol]', '!==', 'true)', kw, '=', '{}')
        output.end_statement()
        # Read values from the kwargs object for any formal parameters
        if a.has_defaults:
            for dname in Object.keys(a.defaults):
                output.indent()
                output.spaced('if', '(Object.prototype.hasOwnProperty.call(' + kw + ',', '"' + dname + '"))')
                output.with_block(def():
                    output.indent()
                    output.spaced(dname, '=', kw + '.' + dname)
                    output.end_statement()
                    if a.kwargs:
                        output.indent()
                        output.spaced('delete', kw + '.' + dname)
                        output.end_statement()
                )
                output.newline()

    if a.starargs is not undefined:
        # Define the *args parameter, putting in whatever is left after assigning the formal parameters and the options object
        nargs = a.length - offset
        output.indent()
        output.spaced('var', a.starargs.name, '=', 'Array.prototype.slice.call(arguments,', nargs + ')')
        output.end_statement()
        # Remove the options object, if present
        output.indent()
        output.spaced('if', '(' + kw, '!==', 'null', '&&', 'typeof', kw, '===', '"object"', '&&', kw, '[ρσ_kwargs_symbol]', '===', 'true)', a.starargs.name)
        output.print('.pop()')
        output.end_statement()

def has_annotations(self):
    if self.return_annotation:
        return True
    for arg in self.argnames:
        if arg.annotation:
            return True
    return False

def function_annotation(self, output, strip_first, name):
    fname = name or (self.name.name if self.name else anonfunc)
    props = Object.create(None)

    # Create __annotations__
    if has_annotations(self):
        props.__annotations__ = def():
            output.print('{')
            if self.argnames and self.argnames.length:
                for i, arg in enumerate(self.argnames):
                    if arg.annotation:
                        arg.print(output)
                        output.print(':'), output.space()
                        arg.annotation.print(output)
                        if i < self.argnames.length - 1 or self.return_annotation:
                            output.comma()
            if self.return_annotation:
                output.print('return:'), output.space()
                self.return_annotation.print(output)
            output.print('}')

    # Create __defaults__
    defaults = self.argnames.defaults
    dkeys = Object.keys(self.argnames.defaults)
    if dkeys.length:
        props.__defaults__ = def():
            output.print('{')
            for i, k in enumerate(dkeys):
                output.print(k + ':'), defaults[k].print(output)
                if i is not dkeys.length - 1:
                    output.comma()
            output.print('}')

    # Create __handles_kwarg_interpolation__
    if not self.argnames.is_simple_func:
        props.__handles_kwarg_interpolation__ = def():
            output.print('true')

    # Create __argnames__
    if self.argnames.length > (1 if strip_first else 0):
        props.__argnames__ = def():
            output.print('[')
            for i, arg in enumerate(self.argnames):
                if strip_first and i is 0:
                    continue
                output.print(JSON.stringify(arg.name))
                if i is not self.argnames.length - 1:
                    output.comma()
            output.print(']')

    # Create __doc__
    if output.options.keep_docstrings and self.docstrings and self.docstrings.length:
        props.__doc__ = def():
            output.print(JSON.stringify(create_doctring(self.docstrings)))

    props.__module__ = def():
        output.print(module_name)

    names = Object.keys(props)
    output.indent()
    # Only define the properties if they were not already defined, which
    # can happen if the function definition is inside a loop, for example.
    output.spaced('if', '(!' + fname + '.' + names[0] + ')', 'Object.defineProperties(' + fname)
    output.comma()
    output.with_block(def():
        for v'var i = 0; i < names.length; i++':
            name = names[i]
            output.indent(), output.spaced(name, ':', '{value:', ''), props[name](), output.print('}')
            if i < names.length - 1:
                output.print(',')
            output.newline()
    )
    output.print(')'), output.end_statement()


def function_definition(self, output, strip_first, as_expression):
    as_expression = as_expression or self.is_expression or self.is_anonymous
    if as_expression:
        orig_indent = output.indentation()
        output.set_indentation(output.next_indent())
        output.spaced('(function()', '{'), output.newline()
        output.indent(), output.spaced('var', anonfunc, '='), output.space()
    output.print("function"), output.space()
    if self.name:
        self.name.print(output)

    if self.is_generator:
        output.print('()'), output.space()
        output.with_block(def():
            if output.options.js_version >= 6:
                output.indent()
                output.print('function* js_generator')
                function_args(self.argnames, output, strip_first)
                print_bracketed(self, output, True, function_preamble)
            else:
                temp = OutputStream({'beautify':True})
                temp.print('function* js_generator')
                function_args(self.argnames, temp, strip_first)
                print_bracketed(self, temp, True, function_preamble)
                transpiled = regenerate(temp.get(), output.options.beautify).replace(/regeneratorRuntime.(wrap|mark)/g, 'ρσ_regenerator.regeneratorRuntime.$1')
                if output.options.beautify:
                    ci = output.make_indent(0)
                    transpiled = [ci + x for x in transpiled.split('\n')].join('\n')
                output.print(transpiled)
            output.newline()
            output.indent()
            output.spaced('var', 'result', '=', 'js_generator.apply(this,', 'arguments)')
            output.end_statement()
            # Python's generator objects use a separate method to send data to the generator
            output.indent()
            output.spaced('result.send', '=', 'result.next')
            output.end_statement()
            output.indent()
            output.spaced('return', 'result')
            output.end_statement()
        )
    else:
        function_args(self.argnames, output, strip_first)
        print_bracketed(self, output, True, function_preamble)

    if as_expression:
        output.end_statement()
        function_annotation(self, output, strip_first, anonfunc)
        output.indent(), output.spaced('return', anonfunc), output.end_statement()
        output.set_indentation(orig_indent)
        output.indent(), output.print("})()")

def print_function(output):
    self = this
    if self.decorators and self.decorators.length:
        output.print("var")
        output.space()
        output.assign(self.name.name)
        decorate(self.decorators, output, def():function_definition(self, output, False, True);)
        output.end_statement()
    else:
        function_definition(self, output, False)
        if not self.is_expression and not self.is_anonymous:
            output.end_statement()
            function_annotation(self, output, False)
# }}}

# Function call {{{

def find_this(expression):
    if is_node_type(expression, AST_Dot):
        return expression.expression
    if not is_node_type(expression, AST_SymbolRef):
        return expression

def print_this(expression, output):
    obj = find_this(expression)
    if obj:
        obj.print(output)
    else:
        output.print('this')

def print_function_call(self, output):
    is_prototype_call = False

    def print_function_name(no_call):
        nonlocal is_prototype_call
        if is_node_type(self, AST_ClassCall):
            # class methods are called through the prototype unless static
            if self.static:
                self.class.print(output)
                output.print(".")
                output.print(self.method)
            else:
                is_prototype_call = True
                self.class.print(output)
                output.print(".prototype.")
                output.print(self.method)
                if not no_call:
                    output.print(".call")
        else:
            if not is_repeatable:
                output.print('ρσ_expr_temp')
                if is_node_type(self.expression, AST_Dot):
                    print_getattr(self.expression, output, True)
            else:
                self.expression.print(output)

    def print_kwargs():
        output.print('ρσ_desugar_kwargs(')
        if has_kwarg_items:
            for i, kwname in enumerate(self.args.kwarg_items):
                if i > 0:
                    output.print(',')
                    output.space()
                kwname.print(output)
            if has_kwarg_formals:
                output.print(',')
                output.space()

        if has_kwarg_formals:
            output.print('{')
            for i, pair in enumerate(self.args.kwargs):
                if i: output.comma()
                pair[0].print(output)
                output.print(':')
                output.space()
                pair[1].print(output)
            output.print('}')
        output.print(')')

    def print_new(apply):
        output.print('ρσ_interpolate_kwargs_constructor.call(')
        output.print('Object.create('), self.expression.print(output), output.print('.prototype)')
        output.comma()
        output.print('true' if apply else 'false')
        output.comma()

    def do_print_this():
        if not is_repeatable:
            output.print('ρσ_expr_temp')
        else:
            print_this(self.expression, output)
        output.comma()

    def print_positional_args():
        # basic arguments
        i = 0
        while i < self.args.length:
            expr = self.args[i]
            is_first = i is 0
            if not is_first:
                output.print('.concat(')
            if expr.is_array:
                expr.print(output)
                i += 1
            else:
                output.print('[')
                while i < self.args.length and not self.args[i].is_array:
                    self.args[i].print(output)
                    if i + 1 < self.args.length and not self.args[i+1].is_array:
                        output.print(',')
                        output.space()
                    i += 1
                output.print(']')
            if not is_first:
                output.print(')')

    has_kwarg_items = self.args.kwarg_items and self.args.kwarg_items.length
    has_kwarg_formals = self.args.kwargs and self.args.kwargs.length
    has_kwargs = has_kwarg_items or has_kwarg_formals
    is_new = is_node_type(self, AST_New)
    is_repeatable = True

    if is_new and not self.args.length and not has_kwargs and not self.args.starargs:
        output.print('new'), output.space()
        print_function_name()
        return # new A is the same as new A() in javascript

    if not has_kwargs and not self.args.starargs:
        # A simple function call, do nothing special
        if is_new:
            output.print('new'), output.space()
        print_function_name()
        output.with_parens(def():
            for i, a in enumerate(self.args):
                if i:
                    output.comma()
                a.print(output)
        )
        return

    is_repeatable = is_new or not has_calls(self.expression)
    if not is_repeatable:
        output.assign('(ρσ_expr_temp'), print_this(self.expression, output), output.comma()

    if has_kwargs:
        if is_new:
            print_new(False)
        else:
            output.print('ρσ_interpolate_kwargs.call(')
            do_print_this()
        print_function_name(True)
        output.comma()
    else:
        if is_new:
            print_new(True)
            print_function_name(True)
            output.comma()
        else:
            print_function_name(True)
            output.print('.apply(')
            do_print_this()

    if is_prototype_call and self.args.length > 1:
        self.args.shift()

    print_positional_args()

    if has_kwargs:
        if self.args.length:
            output.print('.concat(')
        output.print('[')
        print_kwargs()
        output.print(']')
        if self.args.length:
            output.print(')')

    output.print(')')
    if not is_repeatable:
        output.print(')')
# }}}
