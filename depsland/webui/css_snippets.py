import re
from textwrap import dedent


def gradient_border(
        start: str,
        end: str,
        bg: str,
        radius: str = '12px',
) -> str:
    return format('''
        border: 2px solid transparent;
        border-radius: $border_radius;
        background-clip: padding-box, border-box;
        background-origin: padding-box, border-box;
        background-image:
            linear-gradient(to right, $win_bg, $win_bg),
            linear-gradient(90deg, $gradient_start, $gradient_end);
    ''', {
        'win_bg'        : bg,
        'gradient_start': start,
        'gradient_end'  : end,
        'border_radius' : radius,
    })


# def gradient_border_2(
#         class_: str,
#         start: str,
#         end: str,
# ) -> str:
#     return format('''
#         $class_ {
#             border: 2px solid transparent;
#             border-radius: 12px;
#             position: relative;
#             background-color:
#         }
#     ''')


# noinspection PyShadowingBuiltins
def format(text: str, kwargs: dict) -> str:
    pattern = re.compile(r'\$\w+')
    return pattern.sub(lambda x: kwargs[x.group()[1:]], dedent(text))
