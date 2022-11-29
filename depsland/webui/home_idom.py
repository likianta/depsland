import re
import typing as t
from contextlib import contextmanager
from textwrap import dedent

from argsense import cli
from flask import Flask as FlaskApp
from idom import component
from idom import html as h
from idom.backend import flask as flask_impl
from lk_utils import xpath

from depsland.webui import css_snippets as css_snip


class T:
    BackendName = t.Literal['flask', 'tornado']
    Factory = t.Callable
    FactoryArgs = t.List[t.Union[dict, str]]
    Instance = t.Any
    
    FactoryChain = t.List[
        t.Tuple[Factory, t.List[t.Union[Instance, dict, str]]]
    ]


class Context:
    """
    usage:
        ctx = Context()
        with ctx.tag(h.div):
            ctx.add({'class': 'container'})
            with ctx.tag(h.link):
                ctx.add({'rel': 'stylesheet', 'href': ...})
            with ctx.tag(h.button):
                ctx.add({'class': 'button'}, 'click me')
        return ctx.finalize()
    """
    _factory_chain: T.FactoryChain
    _args: t.Optional[T.FactoryArgs]
    _instance: t.Any
    
    def __init__(self):
        self._factory_chain = []
    
    @contextmanager
    def tag(self, factory: T.Factory, style: dict = None) -> t.Iterator[t.Self]:
        self._factory_chain.append(x := (factory, []))
        self._args = x[1]
        if style:
            self._args.append(style)
        yield self
        self._later_init()
        if self._factory_chain:
            self._args = self._factory_chain[-1][1]
        else:
            self._args = None
    
    def add(self, *args: t.Union[dict, str]) -> None:
        self._args.extend(args)
    
    def _later_init(self) -> None:
        factory, args = self._factory_chain.pop()
        self._instance = factory(*args)
        self._factory_chain[-1][1].append(self._instance)
    
    def finalize(self) -> T.Instance:
        if len(self._factory_chain) > 1:
            raise Exception('unclosed tags')
        elif len(self._factory_chain) == 1:
            raise Exception('please exit the `with` block then use this method')
        else:
            return self._instance


ctx = Context()


def _format(text: str, kwargs: dict) -> str:
    pattern = re.compile(r'\$\w+')
    return pattern.sub(lambda x: kwargs[x.group()[1:]], dedent(text))


@component
def index():
    return h.div(
        h.link({'rel': 'stylesheet', 'href': '/static/bulma.min.css'}),
        h.style(_format('''
            
            body {
                background-color: $win_bg;
                height: 100%;
            }
            
            /* hide the browser's scrollbar */
            body::-webkit-scrollbar {
                display: none;
            }
            
            html {
                height: 100%;
            }
            
            .center1 {
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                left: 0;
                margin: auto;
            }
            
            .gradient-border {
                border: 2px solid transparent;
                border-radius: 12px;
                background-clip: padding-box, border-box;
                background-origin: padding-box, border-box;
                background-image:
                    linear-gradient(to right, $win_bg, $win_bg),
                    linear-gradient(90deg, $gradient_start, $gradient_end);
            }
            
            #center-window {
                position: absolute;
                top: 0px;
                right: 0px;
                bottom: 0px;
                left: 0px;
                margin: auto;
            }
        ''', {
            'win_bg'        : '#130f1f',
            'gradient_start': '#673939',
            'gradient_end'  : '#3c2f4f',
        })),
        # h.button(
        #     {'class': 'button'},
        #     'Click me'
        # ),
        h.div(
            {'id'   : 'center-window',
             # 'class': 'gradient-border',
             'style': 'width: 800px; '
                      'height: 640px; '
                      'display: flex; '
                      'flex-direction: column; '
                      'gap: 24px; '
                      'padding: 24px; '
                      'align-items: stretch; '},
            h.div(
                {'id'   : 'title-zone',
                 # 'class': 'title',
                 'style': _dict_2_str({
                     'width'     : '100%',
                     'height'    : '32px',
                     'font-size' : '24px',
                     'text-align': 'center',
                     'color'     : '#fefefe',
                 })},
                'Welcome to Depsland'
            ),
            h.div(
                {'id'   : 'subtitle-zone',
                 'style': _dict_2_str({
                     'width'     : '100%',
                     'height'    : '56px',
                     'font-size' : '16px',
                     'text-align': 'left',
                     'color'     : '#7d7da5',
                 })},
                'Depsland is a fundamental infrastructure to install, update '
                'and manage your Python applications.'
            ),
            h.div(
                {'id'   : 'swipped-pages-zone',
                 # 'class': 'gradient-border',
                 'style': _dict_2_str({
                     'width'      : '100%',
                     'flex-grow'  : '1',
                     'display'    : 'flex',
                     'align-items': 'center',
                 }) + css_snip.gradient_border(
                     start='#673939',
                     end='#3c2f4f',
                     bg='#1D1929',
                 )},
                h.style('''
                    .input1 {
                        color: #fefefe;
                        background-color: #1E182E;
                        border: 1px solid #673939;
                        border-radius: 6px;
                    }
                    .input1:focus {
                        border: 2px solid #673939;
                        background-color: #140F23;
                        outline: none;
                    }
                '''),
                h.input(
                    {'placeholder': 'Select an installation path',
                     'class'      : 'input1',
                     'value'      :
                         'C:/Users/Likianta/AppData/Local/Programs/Depsland',
                     'style'      : 'width: 100%; '
                                    'height: 24px; '
                                    'margin: 0 12px; '},
                ),
                # h.div(
                #     {'class' : 'gradient-border',
                #      'position': 'absolute',
                #      'width' : '80%',
                #      'height': '200px'},
                # )
            ),
        ),
    )


def _dict_2_str(d: dict) -> str:
    return ' '.join(f'{k}: {v};' for k, v in d.items())


@cli.cmd()
def run(host: str, port: int, debug=True) -> None:
    print(host, port)
    app = FlaskApp(
        'depsland',
        static_folder=xpath('static'),
        static_url_path='/static',
    )
    if debug:
        print('flask is running in debug mode')
        app.debug = debug
    flask_impl.configure(app, index)
    # setattr(flask_impl, 'create_development_app', lambda: app)
    # idom.run(index, host=host, port=port, implementation=flask_impl)  # noqa


print(':v', __name__)
# the hot-reloading: https://github.com/idom-team/idom/discussions/837
app = FlaskApp(
    __name__,
    static_folder=xpath('static'),
    static_url_path='/static',
)
flask_impl.configure(app, index)

if __name__ == '__main__':
    # cli.run(run)
    # run()
    pass
