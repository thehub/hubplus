from django.template import get_library, Library, InvalidTemplateLibrary, Variable, TemplateSyntaxError, Node, loader, Context
from django.conf import settings

register = Library()

def do_togglable(parser, token) :
    nodelist = parser.parse(('endtogglable',))
    parser.delete_first_token()

    xs = token.split_contents()
    tag_name = xs[0]
    if len(xs) < 2 :
        raise TemplateSyntaxError('%s requires a single argument' % tag_name)

    return TogglableNode(xs[1:], nodelist)

def is_quoted(s,qs=['"',"'"]) :
    return True if (s[0] == s[-1] and s[0] in qs) else False

def strip_quotes(s) :
    return s.strip('"').strip("'").strip('"')

def eval_arg(x, context) :
    if is_quoted(x) : 
        return strip_quotes(x)
    v = Variable(x)
    return v.resolve(context)

class TogglableNode(Node) :
    def __init__(self, arg_list, nodelist) :
        self.arg_list = arg_list
        self.nodelist = nodelist

    def render(self,context):
        inner = self.nodelist.render(context)
        tpl = loader.get_template('plus_lib/togglable.html')
        
        button_name = ' '.join([eval_arg(x,context) for x in self.arg_list])                
        ret = tpl.render(
                       Context({'button_name': button_name,
                                'inner':inner},autoescape=context.autoescape)
                       )
        return ret

register.tag('togglable',do_togglable)
