from lk_utils.textwrap import dedent


def create_launcher(file_i: str, dir_o: str, name: str = None):
    print('linux is not supported creating launcher yet', ':v4p')
    template = dedent('''
        [Desktop Entry]
        Name={name}
        Exec={dir_o}/run.sh
    ''')
