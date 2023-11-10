from django import template
from django.template.loader_tags import do_extends
import tokenize
from io import StringIO

register = template.Library()

class XExtendsNode(template.Node):
    def __init__(self, node, kwargs):
        self.node = node
        self.kwargs = kwargs

    def render(self, context):
        resolved_kwargs = {key: value.resolve(context) for (key, value) in self.kwargs.items()}
        context.update(resolved_kwargs)
        try:
           return self.node.render(context)
        finally:
           context.pop()

def xextends(parser, token):
    bits = token.contents.split()
    kwargs = {}
    if 'with' in bits:
        pos = bits.index('with')
        argslist = bits[pos+1:]
        bits = bits[:pos]
        for i in argslist:
            try:
                a, b = i.split('=', 1); a = a.strip(); b = b.strip()
                keys = list(tokenize.generate_tokens(StringIO(a).readline))
                if keys[0][0] == tokenize.NAME:
                    kwargs[a] = parser.compile_filter(b)
                else: raise ValueError
            except ValueError:
                raise template.TemplateSyntaxError("Argument syntax wrong: should be key=value")
        token.contents = " ".join(bits)


    xnode = XExtendsNode(do_extends(parser, token), kwargs)

    xnode.node.token = token
    xnode.node.origin = parser.origin
    return xnode


register.tag('xextends', xextends)

def divide(value, divisor):
    try:
        value = float(value)
        divisor = float(divisor)
        if divisor != 0:
            result = value / divisor
            return result
        else:
            return "Division by zero"
    except (ValueError, TypeError) as e:
        return e

register.filter('divide', divide)
