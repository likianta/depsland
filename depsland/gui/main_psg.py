import PySimpleGUI as psg  # noqa

from .. import paths

# psg.theme('SandyBeach')
psg.theme('Light Green 6')


def main():
    layout = [
        [
            psg.Text('Welcome to Depsland!'),
        ],
        [
            psg.Frame('Installed apps', [
                [
                    psg.Text('Hello World'),
                    psg.Text('v0.1.0'),
                    psg.Button('Upgrade'),
                    psg.Button('Launch'),
                ]
            ])
        ],
        [
            psg.Frame('Online apps', [
                [
                    psg.Text('Depsland Testsuit'),
                    psg.Text('v0.1.0'),
                    psg.Button('Install'),
                ]
            ])
        ],
    ]
    
    win = psg.Window('Depsland', layout, icon=paths.build.launcher_ico)
    _mainloop(win)


def _mainloop(win: psg.Window) -> None:
    while True:
        evt, val = win.read()
        print(evt, val, ':l')
        if evt in (None, 'Exit'):
            break
        elif evt == 'Upgrade':
            pass
        elif evt == 'Launch':
            pass
        elif evt == 'Install':
            pass


if __name__ == '__main__':
    main()
